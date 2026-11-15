"""The UI companion stays separate, generated and covered by link validation."""

from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import render
from check import collect_links


class CompanionTests(unittest.TestCase):
    def test_ui_catalog_cannot_be_used_as_the_writing_inventory(self):
        with self.assertRaisesRegex(ValueError, "Unknown category: UI design"):
            render.load_catalog(render.ROOT / "ui/catalog.json")

    def test_check_rejects_a_stale_companion_even_when_main_is_current(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "ui").mkdir()
            for name in ("catalog.json", "ui/catalog.json"):
                (root / name).write_bytes((render.ROOT / name).read_bytes())
            with patch.object(render, "ROOT", root), patch("sys.argv", ["render.py"]):
                render.main()
                (root / "ui/README.md").write_text("Stale companion\n")
                errors = StringIO()
                with patch("sys.argv", ["render.py", "--check"]), redirect_stderr(errors):
                    with self.assertRaises(SystemExit) as result:
                        render.main()
                self.assertEqual(result.exception.code, 1)
                self.assertIn("ui/README.md is stale", errors.getvalue())

    def test_companion_links_are_checked_relative_to_the_companion(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "ui").mkdir()
            main, ui = root / "README.md", root / "ui/README.md"
            main.write_text("# Writing\n[UI](ui/README.md#ui-design)\n")
            ui.write_text("# UI design\n[Back](../README.md)\n[Data](catalog.json)\n[Site](https://example.com/ui)\n")
            (root / "ui/catalog.json").write_text("{}\n")
            urls, errors = collect_links([main, ui])
            self.assertEqual(urls, ["https://example.com/ui"])
            self.assertEqual(errors, [])

    def test_a_root_file_cannot_hide_a_missing_companion_relative_file(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "ui").mkdir()
            (root / "catalog.json").write_text("{}\n")
            ui = root / "ui/README.md"
            ui.write_text("# UI design\n[Data](catalog.json)\n")
            _, errors = collect_links([ui])
            self.assertEqual(len(errors), 1)
            self.assertIn("Missing local file: catalog.json", errors[0])

    def test_anchors_are_checked_in_the_target_document(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "ui").mkdir()
            main, ui = root / "README.md", root / "ui/README.md"
            main.write_text("# UI design\n[UI](ui/README.md#ui-design)\n")
            ui.write_text("# Something else\n")
            _, errors = collect_links([main, ui])
            self.assertEqual(len(errors), 1)
            self.assertIn("Missing section: ui/README.md#ui-design", errors[0])


if __name__ == "__main__":
    unittest.main()
