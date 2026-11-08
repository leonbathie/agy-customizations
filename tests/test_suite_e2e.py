#!/usr/bin/env python3
"""
End-to-End Master Test Suite (test_suite_e2e.py)
Tests the complete integration of the agy-customizations framework:
- Orchestrator integrity
- Sub-skills presence and execution
- Sub-agents manifests and registrar scripts
- Checklists and matrix consistency
"""

import unittest
import subprocess
import sys
from pathlib import Path

FRAMEWORK_ROOT = Path(__file__).resolve().parent.parent

class TestE2EIntegration(unittest.TestCase):
    def test_orchestrator_execution(self):
        orch_script = FRAMEWORK_ROOT / "scripts" / "orchestrator.py"
        res = subprocess.run([sys.executable, str(orch_script), "--all"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Orchestrator failed: {res.stderr}")
        self.assertIn("Overall Health : HEALTHY", res.stdout)
        self.assertIn("SK-01-kernel-architecture", res.stdout)
        self.assertIn("agent-deployer", res.stdout)

    def test_run_matrix_runner(self):
        matrix_script = FRAMEWORK_ROOT / "scripts" / "run_matrix_checks.py"
        res = subprocess.run([sys.executable, str(matrix_script)], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Matrix runner failed: {res.stderr}")
        self.assertIn("7/7 suites validées (100.0%)", res.stdout)

    def test_all_subskills_exist_and_have_skill_md(self):
        sub_skills_dir = FRAMEWORK_ROOT / "sub-skills"
        sub_skills = [
            "SK-01-kernel-architecture",
            "SK-02-rules-engine",
            "SK-03-skill-authoring",
            "SK-04-plugin-packaging",
            "SK-05-lifecycle-hooks",
            "SK-06-mcp-integration",
            "SK-07-deployment-validation"
        ]
        for sk in sub_skills:
            sk_dir = sub_skills_dir / sk
            self.assertTrue(sk_dir.is_dir(), f"Missing sub-skill dir: {sk}")
            self.assertTrue((sk_dir / "SKILL.md").is_file(), f"Missing SKILL.md in: {sk}")
            self.assertTrue((sk_dir / "scripts").is_dir(), f"Missing scripts/ in: {sk}")
            self.assertTrue((sk_dir / "references").is_dir(), f"Missing references/ in: {sk}")
            self.assertTrue((sk_dir / "tests").is_dir(), f"Missing tests/ in: {sk}")

    def test_all_subagents_exist_with_complete_files(self):
        agents_dir = FRAMEWORK_ROOT / "agents"
        agents = [
            "agent-kernel",
            "agent-rules",
            "agent-skill",
            "agent-plugin",
            "agent-hook",
            "agent-mcp",
            "agent-deployer"
        ]
        for ag in agents:
            ag_dir = agents_dir / ag
            self.assertTrue(ag_dir.is_dir(), f"Missing agent dir: {ag}")
            self.assertTrue((ag_dir / "agent.json").is_file(), f"Missing agent.json in: {ag}")
            self.assertTrue((ag_dir / "system_prompt.md").is_file(), f"Missing system_prompt.md in: {ag}")
            self.assertTrue((ag_dir / "registrar.ps1").is_file(), f"Missing registrar.ps1 in: {ag}")

    def test_checklists_and_matrix_exist(self):
        refs = FRAMEWORK_ROOT / "references"
        self.assertTrue((refs / "validation_checklists.md").is_file())
        self.assertTrue((refs / "coverage_matrix.md").is_file())

if __name__ == "__main__":
    unittest.main()
