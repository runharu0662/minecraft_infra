"""Safety checks use synthetic files only; never start Minecraft."""
import hashlib
import importlib.util
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout
import io
import json
import zipfile

REPO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('prepare', REPO / 'scripts/prepare-modpack.py')
prepare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare)


class ExportSafety(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.original_root = prepare.ROOT
        prepare.ROOT = self.root

    def tearDown(self):
        prepare.ROOT = self.original_root
        self.temp.cleanup()

    def archive(self, names):
        path = self.root / '日本語 pack !.zip'
        with zipfile.ZipFile(path, 'w') as archive:
            for name in names:
                archive.writestr(name, b'fixture')
        return path

    def test_traversal_and_windows_paths(self):
        for name in ('../escape', '/absolute', 'C:/escape', 'overrides/../escape', 'x\\..\\escape'):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    prepare.load_export(self.archive([name]))
        self.assertFalse((self.root.parent / 'escape').exists())

    def test_zip_symlink(self):
        path = self.root / 'link.zip'
        with zipfile.ZipFile(path, 'w') as archive:
            info = zipfile.ZipInfo('overrides/config/link')
            info.create_system = 3
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            archive.writestr(info, '/outside')
        with self.assertRaises(ValueError):
            prepare.load_export(path)

    def test_directory_symlink(self):
        source = self.root / 'export'
        source.mkdir()
        (source / 'link').symlink_to(self.root.parent, target_is_directory=True)
        with self.assertRaises(ValueError):
            prepare.load_export(source)

    def test_duplicate_and_unicode_collision(self):
        for names in (['a', 'A'], ['é', 'e\u0301']):
            with self.assertRaises(ValueError):
                prepare.load_export(self.archive(names))

    def test_unicode_filename_is_supported(self):
        self.assertEqual(prepare.load_export(self.archive(['overrides/config/日本語.toml'])),
                         {'overrides/config/日本語.toml': b'fixture'})

    def test_existing_artifact_is_not_overwritten(self):
        path = self.root / 'artifact'
        path.write_bytes(b'original')
        with self.assertRaises(ValueError):
            prepare.write_new_or_same(path, b'replacement')
        self.assertEqual(path.read_bytes(), b'original')

    def test_output_parent_symlink(self):
        (self.root / 'staging').symlink_to(self.root.parent, target_is_directory=True)
        with self.assertRaises(ValueError):
            prepare.write_new_or_same(self.root / 'staging/artifact', b'data')

    def export_directory(self):
        source = self.root / 'source'
        source.mkdir()
        manifest = {'manifestType': 'minecraftModpack', 'manifestVersion': 1,
                    'minecraft': {'version': '1.20.1', 'modLoaders': [{'id': 'forge-47.4.10', 'primary': True}]},
                    'overrides': 'overrides', 'files': [{'projectID': 1, 'fileID': 2, 'required': True}]}
        (source / 'manifest.json').write_text(json.dumps(manifest))
        return source

    def test_custom_output_keeps_source_unchanged_and_is_repeatable(self):
        source = self.export_directory()
        original = (source / 'manifest.json').read_bytes()
        args = ['prepare', str(source), '--staging-dir', str(self.root / 'private/server'),
                '--definition-dir', str(self.root / 'definitions/server')]
        with patch('sys.argv', args), redirect_stdout(io.StringIO()):
            prepare.main()
            prepare.main()
        self.assertEqual((source / 'manifest.json').read_bytes(), original)
        self.assertEqual(list(source.iterdir()), [source / 'manifest.json'])
        self.assertTrue((self.root / 'private/server/server-pack.zip').is_file())
        self.assertTrue((self.root / 'definitions/server/pack.env').is_file())

    def test_output_inside_source_is_rejected(self):
        source = self.export_directory()
        args = ['prepare', str(source), '--staging-dir', str(source / 'output'),
                '--definition-dir', str(self.root / 'definitions')]
        with patch('sys.argv', args), self.assertRaises(ValueError):
            prepare.main()
        self.assertFalse((source / 'output').exists())

    def test_custom_output_outside_repository_is_rejected(self):
        source = self.export_directory()
        args = ['prepare', str(source), '--staging-dir', str(self.root.parent / 'escape'),
                '--definition-dir', str(self.root / 'definitions')]
        with patch('sys.argv', args), self.assertRaises(ValueError):
            prepare.main()


class WorldGuard(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        for folder in ('data/imported-world', 'migration', 'modpack'):
            (self.root / folder).mkdir(parents=True)
        (self.root / 'data/imported-world/level.dat').write_bytes(b'synthetic-test-only')
        (self.root / 'data/server.properties').write_text('level-name=imported-world\n')
        self.pack = self.root / 'modpack/server-pack.zip'
        self.pack.write_bytes(b'archive-fixture')
        self.sha = hashlib.sha256(self.pack.read_bytes()).hexdigest()
        (self.root / 'migration/pack.env').write_text(
            f"PACK_MINECRAFT='1.20.1'\nPACK_FORGE='47.4.10'\nPACK_SHA256='{self.sha}'\n")
        script = (REPO / 'scripts/require-world.sh').read_text()
        for prefix in ('data', 'migration', 'modpack'):
            script = script.replace(f'/{prefix}/', f'{self.root}/{prefix}/')
        # Only the final process handoff is replaced; all actual guards run.
        script = script.replace('exec /start "$@"', 'echo START_REACHED')
        self.script = self.root / 'guard.sh'
        self.script.write_text(script)
        self.env = dict(os.environ, LEVEL='imported-world', VERSION='1.20.1',
                        FORGE_VERSION='47.4.10', MODPACK_VERIFIED_SHA256=self.sha)

    def tearDown(self):
        self.temp.cleanup()

    def check(self, success):
        result = subprocess.run(['sh', str(self.script)], env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, success, result.stderr)
        self.assertEqual('START_REACHED' in result.stdout, success)

    def test_valid_handoff(self):
        self.check(True)

    def test_missing_world(self):
        self.env['LEVEL'] = 'absent'
        self.check(False)

    def test_empty_level(self):
        (self.root / 'data/imported-world/level.dat').write_bytes(b'')
        self.check(False)

    def test_unsafe_name(self):
        self.env['LEVEL'] = '../escape'
        self.check(False)

    def test_symlink_level(self):
        path = self.root / 'data/imported-world/level.dat'
        path.unlink()
        path.symlink_to(self.pack)
        self.check(False)

    def test_properties_mismatch_or_duplicates(self):
        for text in ('level-name=wrong\n',
                     'level-name=imported-world\nlevel-name =wrong\n',
                     'level-name=imported-world\nlevel-name:wrong\n',
                     'motd=continued\\\nlevel-name=imported-world\n'):
            with self.subTest(text=text):
                (self.root / 'data/server.properties').write_text(text)
                self.check(False)

    def test_forge_mismatch(self):
        self.env['FORGE_VERSION'] = '47.0.0'
        self.check(False)

    def test_tampered_archive(self):
        self.pack.write_bytes(b'changed')
        self.check(False)

    def test_unverified_pack(self):
        self.env['MODPACK_VERIFIED_SHA256'] = ''
        self.check(False)


if __name__ == '__main__':
    unittest.main()
