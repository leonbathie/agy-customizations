#!/usr/bin/env python3
"""
Unit Test Suite for SK-04 (Plugin Packaging & Manifests)
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
import sys

current_dir = Path(__file__).resolve().parent
scripts_dir = current_dir.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from bundle_plugin import audit_plugin, package_plugin

class TestPluginPackager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="agy_test_plugin_")
        self.root = Path(self.test_dir)
        self.plugin_dir = self.root / "sample-plugin"
        self.plugin_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_valid_plugin(self):
        manifest = {
            "name": "sample-plugin",
            "author": "Antigravity Team",
            "disabled": False
        }
        (self.plugin_dir / "plugin.json").write_text(json.dumps(manifest), encoding="utf-8")
        (self.plugin_dir / "hooks.json").write_text("{}", encoding="utf-8")
        
        skills_dir = self.plugin_dir / "skills" / "sample-skill"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text("---\nname: sample-skill\ndescription: A test skill\n---\n# Sample", encoding="utf-8")

        audit = audit_plugin(self.plugin_dir)
        self.assertTrue(audit["valid"])
        self.assertEqual(audit["name"], "sample-plugin")
        self.assertTrue(audit["has_hooks"])
        self.assertIn("sample-skill", audit["bundled_skills"])

    def test_misplaced_hooks_json_detected(self):
        manifest = {"name": "faulty-plugin"}
        (self.plugin_dir / "plugin.json").write_text(json.dumps(manifest), encoding="utf-8")
        
        # Place in hooks/hooks.json (invalid for native plugins)
        bad_hooks_dir = self.plugin_dir / "hooks"
        bad_hooks_dir.mkdir()
        (bad_hooks_dir / "hooks.json").write_text("{}", encoding="utf-8")

        audit = audit_plugin(self.plugin_dir)
        self.assertFalse(audit["valid"])
        self.assertTrue(any("hooks/hooks.json" in err for err in audit["issues"]))

    def test_packaging_archive(self):
        manifest = {"name": "sample-plugin"}
        (self.plugin_dir / "plugin.json").write_text(json.dumps(manifest), encoding="utf-8")
        
        out_dir = self.root / "dist"
        archive = package_plugin(self.plugin_dir, out_dir)
        self.assertTrue(archive.is_file())
        self.assertTrue(archive.name.endswith(".zip"))

if __name__ == "__main__":
    unittest.main()
