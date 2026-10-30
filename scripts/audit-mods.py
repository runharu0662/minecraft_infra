#!/usr/bin/env python3
"""Read staged Forge JAR metadata without executing it; report missing mandatory server IDs."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import tomllib
import zipfile


def inspect_jar(data, label, rows, dependencies, depth=0):
    if depth > 4 or len(data) > 128 * 1024 * 1024:
        raise ValueError('Nested JAR limit exceeded')
    with zipfile.ZipFile(io.BytesIO(data)) as jar:
        names = set(jar.namelist())
        metadata = {}
        if 'META-INF/mods.toml' in names:
            info = jar.getinfo('META-INF/mods.toml')
            if info.file_size > 2 * 1024 * 1024:
                raise ValueError('Oversized mods.toml')
            metadata = tomllib.loads(jar.read(info).decode('utf-8-sig'))
        version = None
        if 'META-INF/MANIFEST.MF' in names:
            info = jar.getinfo('META-INF/MANIFEST.MF')
            if info.file_size > 2 * 1024 * 1024:
                raise ValueError('Oversized JAR manifest')
            for line in jar.read(info).decode('utf-8', errors='replace').splitlines():
                if line.startswith('Implementation-Version: '):
                    version = line.split(': ', 1)[1]
        mods = [{'id': m['modId'], 'version': m.get('version', 'UNKNOWN').replace('${file.jarVersion}', version or 'UNRESOLVED')}
                for m in metadata.get('mods', [])]
        rows.append({'jar': label, 'sha256': hashlib.sha256(data).hexdigest(), 'mods': mods})
        for owner, deps in metadata.get('dependencies', {}).items():
            for dep in deps:
                if dep.get('mandatory') and dep.get('side', 'BOTH') != 'CLIENT':
                    dependencies.append({'owner': owner, 'id': dep['modId'],
                                         'range': dep.get('versionRange', ''), 'side': dep.get('side', 'BOTH')})
        # Jar-in-Jar libraries can provide otherwise apparently missing Mod IDs.
        nested = [n for n in names if n.startswith('META-INF/jarjar/') and n.endswith('.jar')]
        for name in sorted(nested):
            info = jar.getinfo(name)
            if info.file_size > 128 * 1024 * 1024:
                raise ValueError('Oversized nested JAR')
            inspect_jar(jar.read(info), f'{label}!/{name}', rows, dependencies, depth + 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mods', type=Path, help='Private prepared mods directory')
    args = parser.parse_args()
    paths = sorted(args.mods.glob('*.jar'))
    if not paths:
        raise ValueError('No downloaded Mod JARs; dependency verification has not been performed')
    rows, dependencies = [], []
    for path in paths:
        if path.is_symlink():
            raise ValueError('Symlink JAR is not accepted')
        inspect_jar(path.read_bytes(), path.name, rows, dependencies)
    available = {'minecraft', 'forge'} | {m['id'] for row in rows for m in row['mods']}
    missing = [dep for dep in dependencies if dep['id'] not in available]
    print(json.dumps({'top_level_jars': len(paths), 'jars': rows,
                      'mandatory_server_dependencies': dependencies, 'missing_ids': missing,
                      'limitations': 'Presence check only. Version ranges, compatibility, client-only code and world integrity need review/testing.'},
                     ensure_ascii=False, indent=2))
    return 1 if missing else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(1)
