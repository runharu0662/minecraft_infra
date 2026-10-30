#!/usr/bin/env python3
"""Validate one local export and produce an immutable private ZIP. No extraction or network."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import unicodedata
import zipfile

ROOT = Path(__file__).resolve().parent.parent
MAX_BYTES = 512 * 1024 * 1024
MAX_FILES = 20000
ALLOWED = {'config', 'defaultconfigs', 'datapacks', 'tacz', 'kubejs', 'scripts', 'mods'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_name(name):
    p = PurePosixPath(name)
    if (not name or '\\' in name or ':' in name or p.is_absolute()
            or any(c in name for c in '\x00\r\n')
            or any(part in ('', '.', '..') for part in name.rstrip('/').split('/'))):
        raise ValueError(f'Unsafe archive path: {name!r}')
    return p.as_posix()


def no_links(path):
    current = path
    while current != ROOT:
        if current.is_symlink():
            raise ValueError(f'Symlink not allowed: {current.name}')
        if current == current.parent:
            raise ValueError('Path must be inside the repository')
        current = current.parent


def load_export(source):
    """Read without extracting; reject links, ambiguous paths, and resource bombs."""
    no_links(source)
    source.resolve().relative_to(ROOT)
    files = {}
    names = set()
    total = 0

    def add(name, size, reader):
        nonlocal total
        name = safe_name(name)
        key = unicodedata.normalize('NFC', name).casefold()
        if key in names:
            raise ValueError(f'Duplicate/case/Unicode collision: {name!r}')
        names.add(key)
        total += size
        if len(names) > MAX_FILES or total > MAX_BYTES:
            raise ValueError('Export exceeds file count or size limit')
        data = reader()
        if len(data) != size:
            raise ValueError(f'Size mismatch: {name!r}')
        files[name] = data

    if source.is_dir():
        for path in sorted(source.rglob('*')):
            if path.is_symlink():
                raise ValueError(f'Symlink not allowed: {path.relative_to(source)}')
            if path.is_dir():
                continue
            if not stat.S_ISREG(path.stat().st_mode):
                raise ValueError('Only regular files are accepted')
            add(path.relative_to(source).as_posix(), path.stat().st_size, path.read_bytes)
    else:
        with zipfile.ZipFile(source) as archive:
            if len(archive.infolist()) > MAX_FILES:
                raise ValueError('Too many archive entries')
            for info in archive.infolist():
                safe_name(info.filename)
                kind = stat.S_IFMT(info.external_attr >> 16)
                if kind not in (0, stat.S_IFREG, stat.S_IFDIR) or info.flag_bits & 1:
                    raise ValueError(f'Link, special, or encrypted entry: {info.filename!r}')
                if not info.is_dir():
                    add(info.filename, info.file_size, lambda i=info: archive.read(i))
    return files


def definition(files):
    manifest = json.loads(files['manifest.json'].decode('utf-8-sig'))
    if manifest.get('manifestType') != 'minecraftModpack' or manifest.get('manifestVersion') != 1:
        raise ValueError('Expected CurseForge minecraftModpack manifest version 1')
    if manifest.get('overrides') != 'overrides':
        raise ValueError('Expected overrides directory')
    minecraft = manifest['minecraft']['version']
    loaders = manifest['minecraft']['modLoaders']
    if len(loaders) != 1 or not re.fullmatch(r'forge-\d+(?:\.\d+)+', loaders[0]['id']):
        raise ValueError('Expected one exact Forge loader')
    if minecraft != '1.20.1':
        raise ValueError('This deployment requires Minecraft 1.20.1')
    if not loaders[0].get('primary'):
        raise ValueError('Forge must be the primary loader')
    entries = manifest['files']
    seen = set()
    for entry in entries:
        if (type(entry.get('projectID')) is not int or type(entry.get('fileID')) is not int
                or min(entry['projectID'], entry['fileID']) <= 0
                or type(entry.get('required')) is not bool or entry['projectID'] in seen):
            raise ValueError('Invalid or duplicate Mod reference')
        seen.add(entry['projectID'])
    if not entries:
        raise ValueError('Empty Mod list')
    for name in files:
        p = PurePosixPath(name)
        if name in ('manifest.json', 'modlist.html'):
            continue
        if len(p.parts) < 3 or p.parts[0] != 'overrides' or p.parts[1] not in ALLOWED:
            raise ValueError(f'Unexpected export content; review before use: {name!r}')
        if any(part in ('playerdata', 'saves', 'region') for part in p.parts) or p.name == 'level.dat':
            raise ValueError(f'World content not accepted in a Modpack export: {name!r}')
    # Publish only identifiers and selection state, not the pack author's identity or settings.
    return {'minecraft': {'version': minecraft, 'modLoaders': loaders},
            'manifestType': 'minecraftModpack', 'manifestVersion': 1,
            'name': 'private-server', 'version': digest(files['manifest.json'])[:16],
            'author': '', 'overrides': 'overrides',
            'files': [{k: e[k] for k in ('projectID', 'fileID', 'required')} for e in entries]}


def scan(files):
    patterns = {
        'private-key': r'-----BEGIN (?:OPENSSH |RSA |EC )?PRIVATE KEY-----',
        'token': r'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]+|tskey-[A-Za-z0-9-]+|AKIA[A-Z0-9]{16})',
        'identity': r'(?:[A-Za-z]:[\\/](?:Users|ユーザー)[\\/]|/Users/|/home/|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,})',
        'secret-assignment': r'(?im)^\s*[\w.-]*(?:password|api[_-]?key|access[_-]?token|secret)[\w.-]*\s*[:=]\s*["\']?[^\s"\'#,}]{6,}',
    }
    findings = []
    for name, data in files.items():
        if any(s in name.lower() for s in ('fingerprint', 'activity.json', 'bookmarks', 'lookuphistory', '/world/local/')):
            findings.append({'path': name, 'kind': 'local-history-or-machine-metadata'})
        try:
            text = data.decode('utf-8-sig')
        except UnicodeError:
            continue
        for kind, pattern in patterns.items():
            if re.search(pattern, text):
                findings.append({'path': name, 'kind': kind})
    return findings


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def write_new_or_same(path, content):
    no_links(path)
    if path.exists():
        if path.read_bytes() != content:
            raise ValueError(f'Refusing to replace existing artifact: {path.relative_to(ROOT)}')
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as out:
        out.write(content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='One ZIP or extracted export inside this repository')
    parser.add_argument('--staging-dir', type=Path, default=Path('staging'))
    parser.add_argument('--definition-dir', type=Path, default=Path('modpack'))
    args = parser.parse_args()
    source = Path(os.path.abspath(args.source))
    files = load_export(source)
    manifest = definition(files)
    findings = scan(files)
    counts = {}
    for name in files:
        p = PurePosixPath(name)
        if p.parts[0] == 'overrides':
            counts[p.parts[1]] = counts.get(p.parts[1], 0) + 1
    stage = Path(os.path.abspath(args.staging_dir))
    definitions = Path(os.path.abspath(args.definition_dir))
    no_links(stage)
    no_links(definitions)
    if source.is_dir() and any(p == source or source in p.parents for p in (stage, definitions)):
        raise ValueError('Output directories must not be inside the source export')
    stage.mkdir(parents=True, exist_ok=True)
    # Archive stored without compression: deterministic across zlib versions.
    import io
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_STORED) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, data)
    archive_bytes = buffer.getvalue()
    lock = {'schema': 1, 'archive_sha256': digest(archive_bytes),
            'minecraft': manifest['minecraft']['version'],
            'forge': manifest['minecraft']['modLoaders'][0]['id'].removeprefix('forge-'),
            'manifest_sha256': digest(files['manifest.json']),
            'references': len(manifest['files']),
            'required': sum(e['required'] for e in manifest['files']),
            'overrides_files': counts}
    # Check all existing artifacts before writing any (no implicit pack upgrades).
    outputs = {
        definitions / 'manifest.json': json_bytes(manifest),
        definitions / 'pack.lock.json': json_bytes(lock),
        definitions / 'pack.env': (
            f"PACK_MINECRAFT='{lock['minecraft']}'\nPACK_FORGE='{lock['forge']}'\n"
            f"PACK_SHA256='{lock['archive_sha256']}'\n").encode(),
        stage / 'server-pack.zip': archive_bytes,
        stage / 'inspection.json': json_bytes({'findings': findings,
            'scope': 'Heuristic text/path scan; not a guarantee of absence of secrets',
            'source_files': {n: digest(d) for n, d in sorted(files.items())}}),
    }
    for path, content in outputs.items():
        no_links(path)
        if path.exists() and path.read_bytes() != content:
            raise ValueError(f'Existing artifact differs; use a separate release checkout: {path.relative_to(ROOT)}')
    for path, content in outputs.items():
        write_new_or_same(path, content)
    for name in ('downloads', 'prepared'):
        target = stage / name
        no_links(target)
        target.mkdir(exist_ok=True)
    print(f"Validated {lock['minecraft']} / Forge {lock['forge']}: {lock['references']} references, {lock['required']} required")
    print(f'Overrides file counts: {counts}')
    print(f'Private scan findings: {len(findings)}; paths only in {stage.relative_to(ROOT)}/inspection.json')
    print(f'Prepared {stage.relative_to(ROOT)}/server-pack.zip; no Minecraft process started or world touched.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, zipfile.BadZipFile) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(1)
