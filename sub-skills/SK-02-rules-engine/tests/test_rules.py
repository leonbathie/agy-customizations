#!/usr/bin/env python3
"""
Unit Test Suite for SK-02 (Rules Engine & Validation)
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

current_dir = Path(__file__).resolve().parent
scripts_dir = current_dir.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from validate_rules import audit_rule_file, scan_and_validate_rules, MAX_BYTES_PER_RULE

class TestRulesEngine(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="agy_test_rules_")
        self.root = Path(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_valid_standalone_rule(self):
        valid_file = self.root / "AGENTS.md"
        valid_file.write_text("# Coding Guidelines\n- Always write tests.", encoding="utf-8")
        
        audit = audit_rule_file(valid_file)
        self.assertTrue(audit["is_valid"])
        self.assertFalse(audit["yaml_violation"])
        self.assertFalse(audit["byte_violation"])

    def test_forbidden_yaml_frontmatter_in_agents_md(self):
        invalid_file = self.root / "AGENTS.md"
        invalid_file.write_text("---\nname: invalid-rule\n---\n# Rule", encoding="utf-8")
        
        audit = audit_rule_file(invalid_file)
        self.assertFalse(audit["is_valid"])
        self.assertTrue(audit["yaml_violation"])

    def test_byte_limit_exceeded(self):
        heavy_file = self.root / "AGENTS.md"
        # Write > 24000 bytes
        heavy_file.write_text("A" * (MAX_BYTES_PER_RULE + 500), encoding="utf-8")
        
        audit = audit_rule_file(heavy_file)
        self.assertFalse(audit["is_valid"])
        self.assertTrue(audit["byte_violation"])

    def test_include_resolution(self):
        sub_doc = self.root / "sub.md"
        sub_doc.write_text("Sub content included successfully.", encoding="utf-8")
        
        main_rule = self.root / "AGENTS.md"
        main_rule.write_text("# Main\n@[SubDoc](./sub.md)", encoding="utf-8")
        
        audit = audit_rule_file(main_rule)
        self.assertTrue(audit["is_valid"])
        self.assertEqual(len(audit["warnings"]), 0)

if __name__ == "__main__":
    unittest.main()
