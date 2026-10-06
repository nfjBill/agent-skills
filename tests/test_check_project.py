"""Check migration inventory behavior using isolated consumer projects."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'skills/ark-v1-upgrade/scripts/check_project.py'


class NodeVersionInventoryTest(unittest.TestCase):
    def setUp(self):
        self.project = tempfile.TemporaryDirectory()
        self.addCleanup(self.project.cleanup)
        self.root = Path(self.project.name)

    def write(self, name, text):
        file = self.root / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(text)
        return file

    def inspect(self):
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.root)],
                                capture_output=True, text=True, check=True)
        return json.loads(result.stdout)

    def test_custom_nvm_and_nested_version_files_are_reported_without_writes(self):
        files = [self.write('.nvm', '# project Node\nv20.10.0\n'),
                 self.write('apps/one/.nvmrc', '20.19.0\n'),
                 self.write('apps/two/.node-version', '22.12.0\n'),
                 self.write('package.json', '{"name":"consumer","engines":{"node":">=18"}}')]
        before = {str(file): hashlib.sha256(file.read_bytes()).hexdigest() for file in files}
        result = self.inspect()
        versions = {entry['file']: entry for entry in result['nodeVersionFiles']}
        self.assertEqual(versions['.nvm']['requested'], 'v20.10.0')
        self.assertEqual(versions['.nvm']['status'], 'incompatible')
        self.assertEqual(versions['apps/one/.nvmrc']['status'], 'compatible')
        self.assertEqual(versions['apps/two/.node-version']['status'], 'compatible')
        self.assertTrue(any(entry['file'] == '.nvm' for entry in result['review']))
        self.assertEqual(result['packages'][0]['node'], '>=18')
        self.assertEqual({str(file): hashlib.sha256(file.read_bytes()).hexdigest() for file in files}, before)

    def test_configured_versions_follow_the_actual_ark_engine_boundaries(self):
        cases = {'18.20.8': 'incompatible', '20.18.3': 'incompatible',
                 '20.19.0': 'compatible', '21.7.3': 'incompatible',
                 '22.11.0': 'incompatible', '22.12.0': 'compatible',
                 '24.0.0': 'compatible', '20.19.0-rc.1': 'needs-review',
                 '20.019.0': 'needs-review'}
        for index, (version, status) in enumerate(cases.items()):
            self.write(f'apps/{index}/.nvm', version + '\n')
        result = self.inspect()
        actual = {entry['requested']: entry['status'] for entry in result['nodeVersionFiles']}
        self.assertEqual(actual, cases)

    def test_floating_selectors_require_resolution_instead_of_assuming_compatibility(self):
        values = ['v20', '20.19', 'lts/*', 'lts/jod', 'node', 'system']
        for index, value in enumerate(values):
            self.write(f'apps/{index}/.nvmrc', value + '\n')
        result = self.inspect()
        self.assertEqual({entry['requested'] for entry in result['nodeVersionFiles']}, set(values))
        self.assertTrue(all(entry['status'] == 'needs-resolution' for entry in result['nodeVersionFiles']))
        self.assertEqual(len(result['review']), len(values))

    def test_unknown_file_content_is_not_executed_or_echoed(self):
        marker = self.root / 'should-not-exist'
        self.write('.nvm', f'node=$(touch {marker}); secret-value\n')
        self.write('.env', 'TOKEN=private-env-value\n')
        self.write('apps/empty/.nvmrc', '# no selected version\n')
        result = self.inspect()
        self.assertTrue(all(entry['status'] == 'needs-review' for entry in result['nodeVersionFiles']))
        self.assertFalse(marker.exists())
        self.assertNotIn('secret-value', json.dumps(result))
        self.assertNotIn('private-env-value', json.dumps(result))

    def test_generated_dependencies_and_symlinks_are_excluded(self):
        self.write('.nvm', '22.12.0\n')
        for directory in ['node_modules', '.git', 'dist', 'artifacts', 'tmp']:
            self.write(directory + '/dependency/.nvm', '18.0.0\n')
        (self.root / 'linked-project').symlink_to(self.root / 'node_modules/dependency', target_is_directory=True)
        result = self.inspect()
        self.assertEqual(result['nodeVersionFiles'], [
            {'file': '.nvm', 'requested': '22.12.0', 'status': 'compatible'}])


if __name__ == '__main__':
    unittest.main()
