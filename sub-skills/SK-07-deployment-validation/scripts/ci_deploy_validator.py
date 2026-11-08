#!/usr/bin/env python3
"""
SK-07 Helper Script: ci_deploy_validator.py
Validateur CI/CD et auditeur des manifestes déclaratifs de déploiement (skills.json, plugins.json) :
- Validation syntaxique et structurelle d'héritage
- Résolution stricte des chemins (absolus, home ~, relatifs workspace)
- Contrôle de cohérence pour intégration continue
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List

def resolve_declared_path(path_str: str, workspace_root: Path) -> Path:
    p_str = path_str.strip()
    if p_str.startswith("~"):
        return Path(os.path.expanduser(p_str)).resolve()
    p = Path(p_str)
    if p.is_absolute():
        return p.resolve()
    return (workspace_root / p).resolve()

def audit_json_config(config_path: Path, workspace_root: Path) -> Dict[str, Any]:
    issues: List[str] = []
    warnings: List[str] = []
    
    if not config_path.is_file():
        return {"valid": False, "issues": [f"Fichier {config_path} introuvable."], "warnings": []}
        
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"valid": False, "issues": [f"JSON invalide dans {config_path.name}: {e}"], "warnings": []}
        
    if not isinstance(data, dict):
        return {"valid": False, "issues": ["Le manifeste JSON doit être un objet."], "warnings": []}

    entries = data.get("entries", [])
    inherits = data.get("inherits", [])
    
    if not isinstance(entries, list) or not isinstance(inherits, list):
        issues.append("'entries' et 'inherits' doivent être des listes.")
        return {"valid": False, "issues": issues, "warnings": warnings}

    resolved_entries = []
    for idx, ent in enumerate(entries):
        if not isinstance(ent, dict) or "path" not in ent:
            issues.append(f"L'entrée entries[{idx}] requiert une propriété 'path'.")
            continue
        p = resolve_declared_path(ent["path"], workspace_root)
        resolved_entries.append({
            "declared": ent["path"],
            "resolved": str(p),
            "exists": p.exists(),
            "include_only": ent.get("include_only"),
            "exclude": ent.get("exclude")
        })
        if not p.exists():
            warnings.append(f"Chemin déclaré inexistant dans entries[{idx}]: {ent['path']} (Résolu: {p})")

    resolved_inherits = []
    for idx, inh in enumerate(inherits):
        if not isinstance(inh, dict) or "path" not in inh:
            issues.append(f"L'héritage inherits[{idx}] requiert une propriété 'path'.")
            continue
        p = resolve_declared_path(inh["path"], workspace_root)
        resolved_inherits.append({
            "declared": inh["path"],
            "resolved": str(p),
            "exists": p.exists(),
            "include_only": inh.get("include_only"),
            "exclude": inh.get("exclude")
        })
        if not p.exists():
            warnings.append(f"Fichier hérité inexistant dans inherits[{idx}]: {inh['path']} (Résolu: {p})")

    return {
        "valid": len(issues) == 0,
        "config_file": str(config_path.resolve()),
        "entries": resolved_entries,
        "inherits": resolved_inherits,
        "issues": issues,
        "warnings": warnings
    }

def main():
    parser = argparse.ArgumentParser(description="Antigravity CI Deployment Validator")
    parser.add_argument("--config", type=str, help="Path to skills.json or plugins.json")
    parser.add_argument("--workspace-root", type=str, default=".", help="Root of repository")
    parser.add_argument("--strict-ci", action="store_true", help="Fail on warnings as well as errors")
    args = parser.parse_args()

    ws_root = Path(args.workspace_root).resolve()
    
    # Target file
    if args.config:
        targets = [Path(args.config)]
    else:
        # Auto-discover in workspace root
        targets = [
            ws_root / ".agents" / "skills.json",
            ws_root / ".agents" / "plugins.json"
        ]
        targets = [t for t in targets if t.is_file()]

    if not targets:
        print("[!] Aucun fichier de configuration déclaratif (skills.json / plugins.json) trouvé.")
        sys.exit(0)

    overall_success = True
    for t in targets:
        report = audit_json_config(t, ws_root)
        print("=" * 70)
        print(f"AUDIT DU MANIFESTE : {t.name}")
        print("=" * 70)
        print(f"Path : {report['config_file']}")
        print(f"Entries count   : {len(report['entries'])}")
        print(f"Inherits count  : {len(report['inherits'])}")
        print("-" * 70)

        for iss in report["issues"]:
            print(f"[!] ERROR: {iss}")
        for w in report["warnings"]:
            print(f"[!] WARN : {w}")

        has_failure = not report["valid"] or (args.strict_ci and len(report["warnings"]) > 0)
        if has_failure:
            overall_success = False

        print(f"Status: {'PASS' if not has_failure else 'FAIL'}")

    print("=" * 70)
    print(f"FINAL CI STATUS: {'PASS' if overall_success else 'FAIL'}")
    print("=" * 70)

    sys.exit(0 if overall_success else 1)

if __name__ == "__main__":
    main()
