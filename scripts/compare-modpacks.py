#!/usr/bin/env python3
"""Read-only export/source-inventory comparison. JSON to stdout; no Minecraft execution."""
import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import sys
import unicodedata

spec = importlib.util.spec_from_file_location('prepare_modpack', Path(__file__).with_name('prepare-modpack.py'))
pack = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pack)


class ModLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.slugs = []

    def handle_starttag(self, tag, attrs):
        url = dict(attrs).get('href', '')
        if tag == 'a' and url.startswith('https://www.curseforge.com/minecraft/mc-mods/'):
            self.slugs.append(url.rstrip('/').split('/')[-1])


def read_export(source):
    files = pack.load_export(source.absolute())
    manifest = pack.definition(files)
    parser = ModLinks()
    parser.feed(files.get('modlist.html', b'').decode('utf-8-sig'))
    return files, manifest, set(parser.slugs)


def overrides(files, normalize=False):
    result = {}
    for name, data in files.items():
        if name.startswith('overrides/'):
            key = unicodedata.normalize('NFC', name) if normalize else name
            if key in result:
                raise ValueError('Unicode collision in overrides')
            result[key] = hashlib.sha256(data).hexdigest()
    return result


def diff_maps(old, new):
    return {'added': sorted(new.keys() - old.keys()), 'removed': sorted(old.keys() - new.keys()),
            'changed': sorted(k for k in old.keys() & new.keys() if old[k] != new[k]),
            'unchanged_count': sum(old[k] == new[k] for k in old.keys() & new.keys())}


def compare_exports(old_source, new_source):
    old_files, old, old_slugs = read_export(old_source)
    new_files, new, new_slugs = read_export(new_source)
    old_refs = {e['projectID']: e for e in old['files']}
    new_refs = {e['projectID']: e for e in new['files']}
    ref_diff = diff_maps(old_refs, new_refs)
    return {'schema': 1, 'old': {'minecraft': old['minecraft'], 'references': len(old_refs)},
            'new': {'minecraft': new['minecraft'], 'references': len(new_refs)},
            'references': {k: v for k, v in ref_diff.items()},
            'added_references': [new_refs[i] for i in ref_diff['added']],
            'removed_references': [old_refs[i] for i in ref_diff['removed']],
            'changed_references': [{'old': old_refs[i], 'new': new_refs[i]} for i in ref_diff['changed']],
            'modlist_slugs': {'added': sorted(new_slugs-old_slugs), 'removed': sorted(old_slugs-new_slugs)},
            'overrides_raw_paths': diff_maps(overrides(old_files), overrides(new_files)),
            'overrides_nfc_paths': diff_maps(overrides(old_files, True), overrides(new_files, True)),
            'new_override_counts': dict(Counter(k.split('/')[1] for k in new_files if k.startswith('overrides/'))),
            'new_scan_findings': pack.scan(new_files),
            'world_verified': False}


def compare_inventory(inventory, export, cache):
    _, manifest, _ = read_export(export)
    source = json.loads(inventory.read_text(encoding='utf-8-sig'))
    if source.get('schema') != 1 or not isinstance(source.get('files'), list):
        raise ValueError('Expected inventory schema 1')
    actual = source['files']
    names = set()
    for item in actual:
        if not isinstance(item.get('name'), str) or item['name'].casefold() in names:
            raise ValueError('Invalid or duplicate inventory filename')
        names.add(item['name'].casefold())
        if (not isinstance(item.get('sha1'), str) or len(item['sha1']) != 40
                or any(c not in '0123456789abcdef' for c in item['sha1'].lower())
                or type(item.get('enabled')) is not bool):
            raise ValueError('Inventory needs SHA-1 hashes and enabled flags')
    metadata = {}
    for root in ([cache] if isinstance(cache, Path) else cache):
        for file in (root / 'getModFileInfo').glob('*.json'):
            data = json.loads(file.read_text())
            key = (data['modId'], data['id'])
            if key in metadata and metadata[key].get('hashes') != data.get('hashes'):
                raise ValueError('Conflicting metadata for the same fixed project/file ID')
            metadata[key] = data
    if not metadata:
        raise ValueError('No official CurseForge file metadata cache available')
    consumed = set()
    matched, missing, different, unknown, states = [], [], [], [], []
    for entry in manifest['files']:
        key = (entry['projectID'], entry['fileID'])
        info = metadata.get(key)
        if info is None:
            unknown.append(entry)
            continue
        hashes = [h['value'].lower() for h in info.get('hashes', []) if h['algo'] == 1]
        if len(hashes) != 1:
            unknown.append(entry)
            continue
        expectation = dict(entry, name=info['fileName'], sha1=hashes[0])
        matches = [(i, x) for i, x in enumerate(actual) if x['sha1'].lower() == hashes[0]]
        if len(matches) == 1:
            i, item = matches[0]
            consumed.add(i)
            matched.append(dict(expectation, actual_name=item['name'], enabled=item['enabled']))
            if item['enabled'] != entry['required']:
                states.append(dict(expectation, actual_enabled=item['enabled']))
        elif len(matches) > 1:
            different.append(dict(expectation, reason='duplicate byte-identical source JARs'))
            consumed.update(i for i, _ in matches)
        else:
            same_names = [(i, x) for i, x in enumerate(actual)
                          if x['name'].removesuffix('.disabled').casefold() == info['fileName'].casefold()]
            if same_names:
                different.append(dict(expectation, reason='same filename but different hash'))
                consumed.update(i for i, _ in same_names)
            else:
                missing.append(expectation)
    extra = [x for i, x in enumerate(actual) if i not in consumed]
    return {'schema': 1, 'source_files': len(actual), 'export_references': len(manifest['files']),
            'matched': matched, 'missing_from_source': missing, 'extra_in_source': extra,
            'different_or_duplicate': different, 'selection_state_differences': states,
            'unresolved_metadata': unknown,
            'source_matches_export': not (missing or extra or different or states or unknown),
            'world_verified': False,
            'limitations': 'SHA-1 identity comparison against official file metadata, not a server compatibility or world verification. required=false is reported separately; never changes source or pack.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    exports = sub.add_parser('exports')
    exports.add_argument('old', type=Path)
    exports.add_argument('new', type=Path)
    inventory = sub.add_parser('inventory')
    inventory.add_argument('source_inventory', type=Path)
    inventory.add_argument('export', type=Path)
    inventory.add_argument('cache', type=Path, nargs='+', help='Official metadata cache(s), never JAR merge destinations')
    args = parser.parse_args()
    if args.command == 'exports':
        result = compare_exports(args.old, args.new)
    else:
        result = compare_inventory(args.source_inventory, args.export, args.cache)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if args.command == 'exports' or result['source_matches_export'] else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(2)
