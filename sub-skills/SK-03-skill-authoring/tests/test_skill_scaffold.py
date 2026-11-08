#!/usr/bin/env python3
"""
Unit Test Suite for SK-03 (Skill Scaffolding & Validation)
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

current_dir = Path(__file__).resolve().parent
scripts_dir = current_dir.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from scaffold_skill import create_skill, validate_skill

class TestSkillScaffold(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="agy_test_skill_")
        self.root = Path(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_create_and_validate_skill(self):
        skill_name = "test-agent-craft"
        created_path = create_skill(skill_name, self.root)
        
        self.assertTrue(created_path.is_dir())
        self.assertTrue((created_path / "SKILL.md").is_file())
        self.assertTrue((created_path / "scripts" / "helper.py").is_file())
        self.assertTrue((created_path / "references" / "prerequisites.md").is_file())
        
        report = validate_skill(created_path)
        self.assertTrue(report["valid"])
        self.assertTrue(report["has_name"])
        self.assertTrue(report["name_valid"])
        self.assertTrue(report["has_description"])
        self.assertFalse(report["body_too_long"])

    def test_invalid_name_rejected(self):
        with self.assertRaises(ValueError):
            create_skill("Invalid_Name_With_Caps", self.root)

if __name__ == "__main__":
    unittest.main()
