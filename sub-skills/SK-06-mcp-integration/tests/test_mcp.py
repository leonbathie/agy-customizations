#!/usr/bin/env python3
"""
Unit Test Suite for SK-06 (MCP Configuration & Validation)
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

from verify_mcp import audit_mcp_config

class TestMCPIntegration(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="agy_test_mcp_")
        self.root = Path(self.test_dir)
        self.config_file = self.root / "mcp_config.json"

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_valid_stdio_and_http_servers(self):
        cfg = {
            "mcpServers": {
                "local-python": {
                    "command": "python",
                    "args": ["-V"],
                    "env": {"DEBUG": "1"}
                },
                "remote-http": {
                    "url": "https://mcp.company.com/mcp"
                }
            }
        }
        self.config_file.write_text(json.dumps(cfg), encoding="utf-8")

        audit = audit_mcp_config(self.config_file, check_binaries=False)
        self.assertTrue(audit["valid"])
        self.assertEqual(audit["servers_count"], 2)
        self.assertEqual(audit["servers"]["local-python"]["transport"], "stdio")
        self.assertEqual(audit["servers"]["remote-http"]["transport"], "streamable_http")

    def test_invalid_mixed_transport(self):
        cfg = {
            "mcpServers": {
                "invalid-server": {
                    "command": "node",
                    "url": "https://mcp.company.com"
                }
            }
        }
        self.config_file.write_text(json.dumps(cfg), encoding="utf-8")

        audit = audit_mcp_config(self.config_file)
        self.assertFalse(audit["valid"])
        self.assertTrue(any("ne peut pas mélanger" in err for err in audit["issues"]))

if __name__ == "__main__":
    unittest.main()
