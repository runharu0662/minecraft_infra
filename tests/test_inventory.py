import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

REPO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('compare', REPO / 'scripts/compare-modpacks.py')
compare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compare)


class InventoryComparison(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.original_root = compare.pack.ROOT
        compare.pack.ROOT = self.root
        self.export = self.root / 'export.zip'
        manifest = {'manifestType': 'minecraftModpack', 'manifestVersion': 1,
                    'minecraft': {'version': '1.20.1', 'modLoaders': [{'id': 'forge-47.4.10', 'primary': True}]},
                    'overrides': 'overrides', 'files': [{'projectID': 1, 'fileID': 2, 'required': True}]}
        with zipfile.ZipFile(self.export, 'w') as archive:
            archive.writestr('manifest.json', json.dumps(manifest))
        self.cache = self.root / 'cache'
        (self.cache / 'getModFileInfo').mkdir(parents=True)
        self.metadata = self.cache / 'getModFileInfo/file.json'
        self.metadata.write_text(json.dumps({'modId': 1, 'id': 2, 'fileName': 'expected.jar',
                                             'hashes': [{'algo': 1, 'value': 'a'*40}]}))
        self.inventory = self.root / 'inventory.json'

    def tearDown(self):
        compare.pack.ROOT = self.original_root
        self.temp.cleanup()

    def run_comparison(self, files):
        self.inventory.write_text(json.dumps({'schema': 1, 'files': files}))
        before = {str(p): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = compare.compare_inventory(self.inventory, self.export, self.cache)
        after = {str(p): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)
        self.assertFalse(result['world_verified'])
        return result

    def test_exact_match_does_not_verify_world(self):
        result = self.run_comparison([{'name': 'expected.jar', 'sha1': 'a'*40, 'enabled': True}])
        self.assertTrue(result['source_matches_export'])

    def test_missing_and_extra(self):
        result = self.run_comparison([{'name': 'extra.jar', 'sha1': 'b'*40, 'enabled': True}])
        self.assertEqual(len(result['missing_from_source']), 1)
        self.assertEqual(len(result['extra_in_source']), 1)
        self.assertFalse(result['source_matches_export'])

    def test_same_name_different_bytes(self):
        result = self.run_comparison([{'name': 'expected.jar', 'sha1': 'b'*40, 'enabled': True}])
        self.assertEqual(len(result['different_or_duplicate']), 1)
        self.assertFalse(result['source_matches_export'])

    def test_disabled_state(self):
        result = self.run_comparison([{'name': 'expected.jar.disabled', 'sha1': 'a'*40, 'enabled': False}])
        self.assertEqual(len(result['selection_state_differences']), 1)
        self.assertFalse(result['source_matches_export'])

    def test_missing_metadata_does_not_pass(self):
        self.metadata.write_text(json.dumps({'modId': 999, 'id': 999, 'fileName': 'other.jar', 'hashes': []}))
        result = self.run_comparison([])
        self.assertEqual(len(result['unresolved_metadata']), 1)
        self.assertFalse(result['source_matches_export'])

    def test_unicode_only_override_name_difference(self):
        with zipfile.ZipFile(self.export, 'a') as archive:
            archive.writestr('overrides/config/é.txt', 'same')
        other = self.root / 'other.zip'
        with zipfile.ZipFile(other, 'w') as archive, zipfile.ZipFile(self.export) as original:
            archive.writestr('manifest.json', original.read('manifest.json'))
            archive.writestr('overrides/config/e\u0301.txt', 'same')
        result = compare.compare_exports(self.export, other)
        self.assertEqual(len(result['overrides_raw_paths']['added']), 1)
        self.assertEqual(result['overrides_nfc_paths']['unchanged_count'], 1)


if __name__ == '__main__':
    unittest.main()
