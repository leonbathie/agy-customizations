#!/usr/bin/env python3
"""
SK-04 Helper Script: bundle_plugin.py
Validateur structurel et empaqueteur de plugins Antigravity :
- Vérification de plugin.json
- Contrôle de la racine stricte pour hooks.json
- Audit des compétences, règles et serveurs MCP embarqués
- Création d'une archive distribuable (.zip)
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from typing import Dict, Any, List

def audit_plugin(plugin_dir: Path) -> Dict[str, Any]:
    issues: List[str] = []
    warnings: List[str] = []
    
    manifest_path = plugin_dir / "plugin.json"
    if not manifest_path.is_file():
        issues.append("Fichier 'plugin.json' manquant à la racine du plugin.")
        return {"valid": False, "issues": issues, "warnings": warnings}
        
    try:
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        issues.append(f"Erreur de syntaxe JSON dans 'plugin.json': {e}")
        return {"valid": False, "issues": issues, "warnings": warnings}
        
    plugin_name = manifest_data.get("name", plugin_dir.name)
    
    # Check misplaced hooks.json
    misplaced_hooks = plugin_dir / "hooks" / "hooks.json"
    root_hooks = plugin_dir / "hooks.json"
    if misplaced_hooks.is_file() and not root_hooks.is_file():
        issues.append("Règle de découverte violée : hooks.json est placé dans hooks/hooks.json au lieu de la racine du plugin.")
        
    # Check skills
    skills_dir = plugin_dir / "skills"
    bundled_skills = []
    if skills_dir.is_dir():
        for sk in skills_dir.iterdir():
            if sk.is_dir() and (sk / "SKILL.md").is_file():
                bundled_skills.append(sk.name)
                
    # Check rules
    rules_dir = plugin_dir / "rules"
    has_rules = rules_dir.is_dir() and any(rules_dir.glob("*.md"))
    
    # Check MCP
    mcp_file = plugin_dir / "mcp_config.json"
    has_mcp = mcp_file.is_file()

    is_valid = len(issues) == 0
    return {
        "valid": is_valid,
        "name": plugin_name,
        "plugin_dir": str(plugin_dir.resolve()),
        "has_hooks": root_hooks.is_file(),
        "has_mcp": has_mcp,
        "has_rules": has_rules,
        "bundled_skills": bundled_skills,
        "issues": issues,
        "warnings": warnings
    }

def package_plugin(plugin_dir: Path, output_dir: Path) -> Path:
    audit = audit_plugin(plugin_dir)
    if not audit["valid"]:
        raise ValueError(f"Plugin non conforme : {'; '.join(audit['issues'])}")
        
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_base = output_dir / f"plugin-{audit['name']}"
    archive_path = shutil.make_archive(str(archive_base), 'zip', root_dir=plugin_dir)
    return Path(archive_path)

def main():
    parser = argparse.ArgumentParser(description="Antigravity Plugin Packager")
    parser.add_argument("--plugin-dir", type=str, required=True, help="Path to plugin directory")
    parser.add_argument("--output-archive", type=str, help="Directory to save the packaged .zip")
    args = parser.parse_args()

    p_dir = Path(args.plugin_dir).resolve()
    audit = audit_plugin(p_dir)

    print("=" * 70)
    print("ANTIGRAVITY PLUGIN PACKAGING AUDIT (SK-04)")
    print("=" * 70)
    print(f"Plugin Name       : {audit.get('name')}")
    print(f"Plugin Path       : {audit.get('plugin_dir')}")
    print(f"Has Hooks at Root : {audit.get('has_hooks')}")
    print(f"Has MCP Config    : {audit.get('has_mcp')}")
    print(f"Has Rules         : {audit.get('has_rules')}")
    print(f"Bundled Skills    : {audit.get('bundled_skills')}")
    print("-" * 70)

    for issue in audit["issues"]:
        print(f"[!] ERROR: {issue}")
    for warning in audit["warnings"]:
        print(f"[!] WARN : {warning}")

    print("=" * 70)
    print(f"STATUS            : {'PASS' if audit['valid'] else 'FAIL'}")
    print("=" * 70)

    if audit["valid"] and args.output_archive:
        pkg = package_plugin(p_dir, Path(args.output_archive))
        print(f"[OK] Package generated: {pkg}")

    sys.exit(0 if audit["valid"] else 1)

if __name__ == "__main__":
    main()
