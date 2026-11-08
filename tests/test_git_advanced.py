#!/usr/bin/env python3
"""
Unit and Integration Test Suite for Git Advanced Intelligence Engine
"""

import unittest
import sys
from pathlib import Path
import tempfile
import shutil
import re

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.git_advanced_engine import GitEngine, SECRET_PATTERNS

class TestGitAdvancedEngine(unittest.TestCase):
    def setUp(self):
        self.engine = GitEngine(repo_root=ROOT)

    def test_secret_patterns_detection(self):
        # 1. Google API key (AIza followed by 35 characters = 39 total)
        fake_google = "AIzaSyD-fake_key_for_testing_1234567890"
        self.assertEqual(len(fake_google), 39)
        self.assertTrue(any(re.search(pat, fake_google) for pat, _ in SECRET_PATTERNS))

        # 2. GitHub Token
        fake_gh = "ghp_1234567890abcdefghijklmnopqrstuvwxyzAB"
        self.assertTrue(any(re.search(pat, fake_gh) for pat, _ in SECRET_PATTERNS))

        # 3. Private Key
        fake_priv = "-----BEGIN RSA PRIVATE KEY-----"
        self.assertTrue(any(re.search(pat, fake_priv) for pat, _ in SECRET_PATTERNS))

    def test_conventional_commit_syntax(self):
        res = self.engine.generate_smart_commit(hint="add neural network classifier")
        # Should contain type and scope
        self.assertIn("type", res)
        self.assertIn("scope", res)
        self.assertIn("subject", res)
        self.assertIn("add neural network classifier", res["subject"])

    def test_changelog_structure(self):
        res = self.engine.generate_changelog()
        self.assertIn("version", res)
        self.assertIn("content", res)
        self.assertTrue(res["content"].startswith("# CHANGELOG"))

    def test_worktree_listing(self):
        trees = self.engine.list_worktrees()
        self.assertIsInstance(trees, list)
        self.assertGreaterEqual(len(trees), 1)

if __name__ == "__main__":
    unittest.main()
