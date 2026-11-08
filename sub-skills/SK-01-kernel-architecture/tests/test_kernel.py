#!/usr/bin/env python3
"""
Unit Test Suite for SK-01 (Kernel Architecture & Discovery)
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

# Add scripts directory to path
current_dir = Path(__file__).resolve().parent
scripts_dir = current_dir.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from audit_discovery import find_repo_root, scan_hierarchical_customizations, PRECEDENCE_LEVELS

class TestKernelDiscovery(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="agy_test_kernel_")
        self.root = Path(self.test_dir)
        # Create mock git repo
        (self.root / ".git").mkdir()
        # Create nested workspace structure
        self.sub_pkg = self.root / "packages" / "app"
        self.sub_pkg.mkdir(parents=True)
        # Create .agents in sub_pkg
        self.local_agents = self.sub_pkg / ".agents"
        self.local_agents.mkdir()
        (self.local_agents / "skills").mkdir()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_find_repo_root(self):
        detected_root = find_repo_root(self.sub_pkg)
        self.assertEqual(detected_root, self.root)

    def test_hierarchical_scan(self):
        discovered = scan_hierarchical_customizations(self.sub_pkg, self.root)
        self.assertGreaterEqual(len(discovered), 1)
        self.assertEqual(discovered[0]["dot_dir"], ".agents")
        self.assertTrue(discovered[0]["has_skills"])
        self.assertEqual(discovered[0]["precedence_level"], 1)

    def test_precedence_levels_integrity(self):
        self.assertEqual(len(PRECEDENCE_LEVELS), 5)
        self.assertIn("Workspace Project", PRECEDENCE_LEVELS[1])
        self.assertIn("Global Declared", PRECEDENCE_LEVELS[5])

if __name__ == "__main__":
    unittest.main()
