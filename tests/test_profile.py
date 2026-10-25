import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check_profile.py"


class ProfileCheckTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        spec = importlib.util.spec_from_file_location("check_profile", SCRIPT)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        (self.root / "assets").mkdir()
        (self.root / "assets/card.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        (self.root / "START_HERE.md").write_text('[主页](README.md)')

    def readme(self, content):
        (self.root / "README.md").write_text(content)
        return self.module.check_profile(self.root)

    def test_existing_markdown_and_html_assets_and_mode_fragment(self):
        self.assertEqual(self.readme('![card](assets/card.svg)\n<img src="assets/card.svg#gh-dark-mode-only" alt="Card">'), [])

    def test_missing_image_and_empty_alt_are_diagnostics(self):
        errors = self.readme('<img src="missing.svg" alt="">')
        self.assertTrue(any("missing.svg" in error for error in errors))
        self.assertTrue(any("alt" in error for error in errors))

    def test_malformed_svg_is_reported(self):
        (self.root / "assets/card.svg").write_text('<svg>')
        self.assertTrue(any("SVG" in error for error in self.readme('![card](assets/card.svg)')))

    def test_link_escapes_are_rejected(self):
        self.assertTrue(any("outside" in error for error in self.readme('[outside](../external.md)')))

    def test_external_links_are_not_claimed_as_verified(self):
        self.assertEqual(self.readme('[project](https://github.com/hrniux/codex-skills)\n[mail](mailto:example@example.test)'), [])

    def test_starting_guide_local_links_are_checked_with_document_context(self):
        (self.root / "START_HERE.md").write_text('[broken](missing-guide-target.md)')
        errors = self.readme('[开始](START_HERE.md)')
        self.assertTrue(any('START_HERE.md' in error and 'missing-guide-target.md' in error for error in errors))


if __name__ == '__main__':
    unittest.main()
