#!/usr/bin/env python3
"""
Master Orchestrator Script for Antigravity Customizations Framework (agy-customizations)
Coordinates all 7 sub-skills (SK-01 to SK-07) and delegates to specialized sub-agents.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List

FRAMEWORK_ROOT = Path(__file__).resolve().parent.parent

SUB_SKILLS = [
    ("SK-01-kernel-architecture", "sub-skills/SK-01-kernel-architecture/scripts/audit_discovery.py"),
    ("SK-02-rules-engine", "sub-skills/SK-02-rules-engine/scripts/validate_rules.py"),
    ("SK-03-skill-authoring", "sub-skills/SK-03-skill-authoring/scripts/scaffold_skill.py"),
    ("SK-04-plugin-packaging", "sub-skills/SK-04-plugin-packaging/scripts/bundle_plugin.py"),
    ("SK-05-lifecycle-hooks", "sub-skills/SK-05-lifecycle-hooks/scripts/hook_runner.py"),
    ("SK-06-mcp-integration", "sub-skills/SK-06-mcp-integration/scripts/verify_mcp.py"),
    ("SK-07-deployment-validation", "sub-skills/SK-07-deployment-validation/scripts/ci_deploy_validator.py")
]

AGENTS = [
    "agent-kernel",
    "agent-rules",
    "agent-skill",
    "agent-plugin",
    "agent-hook",
    "agent-mcp",
    "agent-deployer"
]

def run_global_audit(target_dir: Path) -> Dict[str, Any]:
    report = {
        "framework_root": str(FRAMEWORK_ROOT),
        "target_directory": str(target_dir.resolve()),
        "sub_skills_count": len(SUB_SKILLS),
        "agents_count": len(AGENTS),
        "sub_skills_status": {},
        "agents_status": {}
    }

    # Verify Sub-skills
    for sk_name, sk_script in SUB_SKILLS:
        sk_path = FRAMEWORK_ROOT / "sub-skills" / sk_name
        sk_md = sk_path / "SKILL.md"
        script_full = FRAMEWORK_ROOT / sk_script
        has_tests = (sk_path / "tests").is_dir() and any((sk_path / "tests").glob("test_*.py"))
        
        report["sub_skills_status"][sk_name] = {
            "has_skill_md": sk_md.is_file(),
            "has_script": script_full.is_file(),
            "has_tests": has_tests,
            "ready": sk_md.is_file() and script_full.is_file() and has_tests
        }

    # Verify Agents
    for ag in AGENTS:
        ag_path = FRAMEWORK_ROOT / "agents" / ag
        has_json = (ag_path / "agent.json").is_file()
        has_prompt = (ag_path / "system_prompt.md").is_file()
        has_reg = (ag_path / "registrar.ps1").is_file()
        
        report["agents_status"][ag] = {
            "has_json": has_json,
            "has_prompt": has_prompt,
            "has_registrar": has_reg,
            "ready": has_json and has_prompt and has_reg
        }

    all_skills_ready = all(v["ready"] for v in report["sub_skills_status"].values())
    all_agents_ready = all(v["ready"] for v in report["agents_status"].values())
    report["overall_health"] = "HEALTHY" if (all_skills_ready and all_agents_ready) else "DEGRADED"

    return report

def main():
    parser = argparse.ArgumentParser(description="Antigravity Customizations Master Orchestrator")
    parser.add_argument("--action", choices=["audit", "status"], default="audit")
    parser.add_argument("--target-dir", type=str, default=".", help="Target workspace directory")
    parser.add_argument("--all", action="store_true", help="Check all components")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    target = Path(args.target_dir).resolve()
    report = run_global_audit(target)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("=" * 75)
        print("ANTIGRAVITY CUSTOMIZATIONS MASTER ORCHESTRATOR")
        print("=" * 75)
        print(f"Framework Root : {report['framework_root']}")
        print(f"Target Scope   : {report['target_directory']}")
        print(f"Overall Health : {report['overall_health']}")
        print("-" * 75)
        print("[*] SUB-SKILLS STATUS (SK-01 to SK-07):")
        for sk, st in report["sub_skills_status"].items():
            status_symbol = "[OK]" if st["ready"] else "[FAIL]"
            print(f"  {status_symbol} {sk:32} | SKILL.md: {st['has_skill_md']} | Script: {st['has_script']} | Tests: {st['has_tests']}")

        print("\n[*] SUB-AGENTS STATUS (agent-kernel to agent-deployer):")
        for ag, st in report["agents_status"].items():
            status_symbol = "[OK]" if st["ready"] else "[FAIL]"
            print(f"  {status_symbol} {ag:32} | JSON: {st['has_json']} | Prompt: {st['has_prompt']} | Registrar: {st['has_registrar']}")
        print("=" * 75)

    sys.exit(0 if report["overall_health"] == "HEALTHY" else 1)

if __name__ == "__main__":
    main()
