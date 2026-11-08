#!/usr/bin/env python3
"""
SK-01 Helper Script: audit_discovery.py
Audite la découverte hiérarchique des personnalisations Antigravity,
la résolution des répertoires pivots, et les 5 niveaux de précédence.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

DOT_DIR_CANDIDATES = [".agents", ".agent", "_agents", "_agent"]

PRECEDENCE_LEVELS = {
    1: "Workspace Project (Hierarchical CWD to Git Root)",
    2: "Declared Configurations (Local skills.json / plugins.json)",
    3: "Global Discovery (~/.gemini/config/)",
    4: "Built-in Customizations (AGY Bundled)",
    5: "Global Declared Configurations (~/.gemini/config/*.json)"
}

def find_repo_root(start_path: Path) -> Path:
    current = start_path.resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".git").exists():
            return parent
    return current

def scan_hierarchical_customizations(start_path: Path, repo_root: Path) -> List[Dict[str, Any]]:
    discovered = []
    current = start_path.resolve()
    
    # Traverse from CWD up to repository root
    chain = []
    curr = current
    while True:
        chain.append(curr)
        if curr == repo_root or curr.parent == curr:
            break
        curr = curr.parent

    for node in chain:
        for candidate in DOT_DIR_CANDIDATES:
            target = node / candidate
            if target.is_dir():
                skills_dir = target / "skills"
                rules_dir = target / "rules"
                plugins_dir = target / "plugins"
                hooks_file = target / "hooks.json"
                mcp_file = target / "mcp_config.json"
                
                discovered.append({
                    "node_path": str(node),
                    "dot_dir": candidate,
                    "full_path": str(target),
                    "has_skills": skills_dir.is_dir(),
                    "has_rules": rules_dir.is_dir(),
                    "has_plugins": plugins_dir.is_dir(),
                    "has_hooks": hooks_file.is_file(),
                    "has_mcp": mcp_file.is_file(),
                    "precedence_level": 1
                })
    return discovered

def scan_global_customizations() -> Dict[str, Any]:
    home = Path.home()
    global_cfg = home / ".gemini" / "config"
    return {
        "global_path": str(global_cfg),
        "exists": global_cfg.is_dir(),
        "has_skills": (global_cfg / "skills").is_dir(),
        "has_plugins": (global_cfg / "plugins").is_dir(),
        "has_hooks": (global_cfg / "hooks.json").is_file(),
        "has_mcp": (global_cfg / "mcp_config.json").is_file(),
        "precedence_level": 3
    }

def run_audit(target_dir: Optional[str] = None, json_output: bool = False) -> Dict[str, Any]:
    start = Path(target_dir).resolve() if target_dir else Path.cwd().resolve()
    repo_root = find_repo_root(start)
    
    hierarchical = scan_hierarchical_customizations(start, repo_root)
    global_disc = scan_global_customizations()
    
    report = {
        "cwd": str(start),
        "repo_root": str(repo_root),
        "is_inside_git": (repo_root / ".git").exists(),
        "hierarchical_nodes_count": len(hierarchical),
        "hierarchical_nodes": hierarchical,
        "global_discovery": global_disc,
        "precedence_resolution_rules": PRECEDENCE_LEVELS
    }
    
    if json_output:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("=" * 70)
        print("ANTIGRAVITY KERNEL DISCOVERY AUDIT (SK-01)")
        print("=" * 70)
        print(f"[*] CWD             : {report['cwd']}")
        print(f"[*] Repo Root       : {report['repo_root']} (Git: {report['is_inside_git']})")
        print(f"[*] Hierarchical Dot-dirs Detected: {len(hierarchical)}")
        for idx, h in enumerate(hierarchical, 1):
            print(f"    [{idx}] {h['dot_dir']} in {h['node_path']}")
            print(f"        Skills: {h['has_skills']} | Rules: {h['has_rules']} | Plugins: {h['has_plugins']} | Hooks: {h['has_hooks']}")
        print(f"[*] Global Config   : {global_disc['global_path']} (Active: {global_disc['exists']})")
        print("=" * 70)
    
    return report

def main():
    parser = argparse.ArgumentParser(description="Antigravity Kernel Discovery Auditor")
    parser.add_argument("--target-dir", type=str, help="Target directory to inspect")
    parser.add_argument("--json", action="store_true", help="Output audit report as JSON")
    args = parser.parse_args()
    
    run_audit(args.target_dir, args.json)

if __name__ == "__main__":
    main()
