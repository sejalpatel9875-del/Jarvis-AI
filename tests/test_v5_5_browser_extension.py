"""
tests/test_v5_5_browser_extension.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Unittest Suite validating JARVIS Browser Extension Files & Manifest V3 Specs.
"""

import unittest
import os
import json


class TestV55BrowserExtension(unittest.TestCase):
    def test_extension_files_exist(self):
        ext_dir = os.path.join(".", "extension")
        self.assertTrue(os.path.exists(os.path.join(ext_dir, "manifest.json")))
        self.assertTrue(os.path.exists(os.path.join(ext_dir, "background", "service_worker.js")))
        self.assertTrue(os.path.exists(os.path.join(ext_dir, "content", "content_script.js")))
        self.assertTrue(os.path.exists(os.path.join(ext_dir, "popup", "popup.html")))
        self.assertTrue(os.path.exists(os.path.join(ext_dir, "popup", "popup.css")))
        self.assertTrue(os.path.exists(os.path.join(ext_dir, "popup", "popup.js")))

    def test_manifest_v3_validity(self):
        manifest_path = os.path.join(".", "extension", "manifest.json")
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data.get("manifest_version"), 3)
        self.assertEqual(data.get("version"), "5.5.0")
        self.assertIn("activeTab", data.get("permissions", []))
        self.assertIn("contextMenus", data.get("permissions", []))
        self.assertEqual(
            data.get("background", {}).get("service_worker"), "background/service_worker.js"
        )
        self.assertEqual(data.get("action", {}).get("default_popup"), "popup/popup.html")


if __name__ == "__main__":
    unittest.main()
