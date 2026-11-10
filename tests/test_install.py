import importlib.util
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('installer', Path(__file__).resolve().parents[1] / 'scripts/install.py')
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='github-first-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def args(self, *extra):
        return installer.parser().parse_args(['--dsh-home', str(self.root / 'dsh'), '--agents-home', str(self.root / 'agents'), '--codex-home', str(self.root / 'codex'), *extra])

    def test_preserves_rules_and_repeated_install_is_noop(self):
        rules = self.root / 'dsh/AGENTS.md'
        rules.parent.mkdir()
        original = b'Existing instructions\r\n'
        rules.write_bytes(original)
        result = installer.install(self.args('--with-rules'))
        after = rules.read_bytes()
        self.assertTrue(after.startswith(original))
        self.assertEqual((Path(result['backup']) / 'AGENTS-0.md').read_bytes(), original)
        again = installer.install(self.args('--with-rules'))
        self.assertEqual(again['rules_updated'], [])
        self.assertEqual(after, rules.read_bytes())

    def test_shared_target_and_both_rules(self):
        result = installer.install(self.args('--target', 'shared', '--with-rules'))
        self.assertEqual(Path(result['skill']), self.root / 'agents/skills/github-first')
        self.assertEqual(len(result['rules_updated']), 2)

    def test_existing_edits_require_update_and_are_backed_up(self):
        result = installer.install(self.args())
        skill = Path(result['skill']) / 'SKILL.md'
        skill.write_text('my custom version', encoding='utf-8')
        with self.assertRaises(ValueError):
            installer.install(self.args())
        updated = installer.install(self.args('--update'))
        self.assertEqual((Path(updated['backup']) / 'skill/SKILL.md').read_text(), 'my custom version')
        self.assertTrue(skill.read_text(encoding='utf-8').startswith('---'))

    def test_bad_markers_fail_before_skill_install(self):
        rules = self.root / 'dsh/AGENTS.md'
        rules.parent.mkdir()
        rules.write_text(installer.BEGIN, encoding='utf-8')
        with self.assertRaises(ValueError):
            installer.install(self.args('--with-rules'))
        self.assertFalse((self.root / 'dsh/skills/github-first').exists())

    def test_managed_update_preserves_surrounding_text(self):
        original = 'before\n' + installer.BEGIN + '\nold\n' + installer.END + '\nafter'
        replacement = installer.BEGIN + '\nnew\n' + installer.END
        self.assertEqual(installer.merge_rules(original, replacement), 'before\n' + replacement + '\nafter')


if __name__ == '__main__':
    unittest.main()
