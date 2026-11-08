#!/usr/bin/env python3
"""
Unit Test Suite for SK-07 (Deployment & Manifest Validation)
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

from ci_deploy_validator import audit_json_config, resolve_declared_path

class TestDeploymentValidation(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="agy_test_deploy_")
        self.root = Path(self.test_dir)
        self.manifest_file = self.root / "skills.json"

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_valid_manifest(self):
        # Create a mock folder
        custom_folder = self.root / "my-skills"
        custom_folder.mkdir()

        cfg = {
            "inherits": [],
            "entries": [
                {
                    "path": "./my-skills",
                    "exclude": ["temp-.*"]
                }
            ]
        }
        self.manifest_file.write_text(json.dumps(cfg), encoding="utf-8")

        report = audit_json_config(self.manifest_file, self.root)
        self.assertTrue(report["valid"])
        self.assertEqual(len(report["entries"]), 1)
        self.assertTrue(report["entries"][0]["exists"])
        self.assertEqual(len(report["warnings"]), 0)

    def test_path_resolution(self):
        rel = resolve_declared_path("./local/path", self.root)
        self.assertEqual(rel, (self.root / "local" / "path").resolve())

        home_rel = resolve_declared_path("~/test_dir", self.root)
        self.assertEqual(home_rel, (Path.home() / "test_dir").resolve())

if __name__ == "__main__":
    unittest.main()
