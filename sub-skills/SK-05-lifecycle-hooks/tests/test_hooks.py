#!/usr/bin/env python3
"""
Unit Test Suite for SK-05 (Lifecycle Hooks)
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

from hook_runner import validate_hooks_file, simulate_trigger

class TestLifecycleHooks(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="agy_test_hooks_")
        self.root = Path(self.test_dir)
        self.hooks_file = self.root / "hooks.json"

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_valid_hooks_configuration(self):
        config = {
            "security-gate": {
                "enabled": True,
                "PreToolUse": [
                    {
                        "matcher": "run_command",
                        "hooks": [
                            {"command": "./scripts/guard.py", "timeout": 5}
                        ]
                    }
                ]
            },
            "session-init": {
                "SessionStart": [
                    {"command": "./scripts/boot.sh"}
                ]
            }
        }
        self.hooks_file.write_text(json.dumps(config), encoding="utf-8")

        audit = validate_hooks_file(self.hooks_file)
        self.assertTrue(audit["valid"])
        self.assertEqual(len(audit["named_hooks"]), 2)

        # Test simulation
        triggered = simulate_trigger(self.hooks_file, "PreToolUse", "run_command")
        self.assertEqual(len(triggered), 1)
        self.assertEqual(triggered[0]["command"], "./scripts/guard.py")

    def test_invalid_flat_structure_for_pretooluse(self):
        # PreToolUse must NOT be flat; it must be grouped
        bad_config = {
            "invalid-hook": {
                "PreToolUse": [
                    {"command": "./bad_structure.sh"}
                ]
            }
        }
        self.hooks_file.write_text(json.dumps(bad_config), encoding="utf-8")

        audit = validate_hooks_file(self.hooks_file)
        self.assertFalse(audit["valid"])
        self.assertTrue(any("requiert le champ 'matcher'" in err for err in audit["issues"]))

if __name__ == "__main__":
    unittest.main()
