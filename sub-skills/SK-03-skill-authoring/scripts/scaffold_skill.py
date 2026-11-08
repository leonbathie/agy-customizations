#!/usr/bin/env python3
"""
SK-03 Helper Script: scaffold_skill.py
Générateur et validateur de compétences (Skills) Antigravity :
- Échafaudage de la structure canonique (scripts, examples, resources, references)
- Validation stricte du frontmatter YAML (name, description)
- Vérification du principe de divulgation progressive
"""

import os
import sys
import re
import argparse
from pathlib import Path
from typing import Dict, Any

FRONTMATTER_REGEX = re.compile(r'^---\s*\n(.*?)\n---\s*\n(.*)$', re.DOTALL)
NAME_REGEX = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')

def create_skill(name: str, target_dir: Path) -> Path:
    if not NAME_REGEX.match(name):
        raise ValueError(f"Skill name '{name}' must be lowercase and hyphenated (e.g. 'my-awesome-skill').")
        
    skill_dir = target_dir / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    
    (skill_dir / "scripts").mkdir(exist_ok=True)
    (skill_dir / "examples").mkdir(exist_ok=True)
    (skill_dir / "resources").mkdir(exist_ok=True)
    (skill_dir / "references").mkdir(exist_ok=True)
    
    skill_md = skill_dir / "SKILL.md"
    content = f"""---
name: {name}
description: >-
  Expertise pour {name}. Activez ce skill dès que l'utilisateur demande
  d'exécuter ou de configurer des opérations liées à {name}.
---

# {name.replace('-', ' ').title()}

Guide pas-à-pas pour l'utilisation de la compétence {name}.

## Étapes Opérationnelles

1. Préparer l'environnement :
   Consulter [Pré-requis](./references/prerequisites.md).
2. Exécuter le script d'aide :
   `python ./scripts/helper.py`
3. Vérifier les résultats dans les journaux d'exécution.
"""
    skill_md.write_text(content, encoding="utf-8")
    
    # Create sample reference
    (skill_dir / "references" / "prerequisites.md").write_text(
        f"# Pré-requis pour {name}\n\nSpécifications et détails techniques volumineux isolés pour préserver le contexte.",
        encoding="utf-8"
    )
    
    # Create sample script
    (skill_dir / "scripts" / "helper.py").write_text(
        f'#!/usr/bin/env python3\nprint("Helper executing for {name}")\n',
        encoding="utf-8"
    )

    return skill_dir

def validate_skill(path: Path) -> Dict[str, Any]:
    skill_md = path / "SKILL.md" if path.is_dir() else path
    if not skill_md.is_file():
        return {
            "valid": False,
            "error": f"Fichier SKILL.md introuvable dans {path}"
        }
        
    content = skill_md.read_text(encoding="utf-8", errors="replace")
    match = FRONTMATTER_REGEX.match(content)
    if not match:
        return {
            "valid": False,
            "error": "Frontmatter YAML manquant ou mal formé (doit commencer et finir par '---')"
        }
        
    frontmatter_text = match.group(1)
    body = match.group(2)
    
    has_name = bool(re.search(r'^name:\s*([a-z0-9\-]+)', frontmatter_text, re.MULTILINE))
    has_desc = bool(re.search(r'^description:\s*(.+)', frontmatter_text, re.MULTILINE))
    
    # Check name format
    name_match = re.search(r'^name:\s*([^\s]+)', frontmatter_text, re.MULTILINE)
    name_valid = bool(name_match and NAME_REGEX.match(name_match.group(1).strip()))
    
    # Check progressive disclosure (body should not be overwhelmingly long)
    body_lines = len(body.splitlines())
    body_too_long = body_lines > 500
    
    is_valid = has_name and has_desc and name_valid and (not body_too_long)

    return {
        "valid": is_valid,
        "skill_dir": str(skill_md.parent.resolve()),
        "has_name": has_name,
        "name_valid": name_valid,
        "has_description": has_desc,
        "body_lines": body_lines,
        "body_too_long": body_too_long,
        "has_scripts": (skill_md.parent / "scripts").is_dir(),
        "has_references": (skill_md.parent / "references").is_dir()
    }

def main():
    parser = argparse.ArgumentParser(description="Skill Scaffolder & Validator")
    parser.add_argument("--action", choices=["create", "validate"], required=True)
    parser.add_argument("--name", type=str, help="Name of the skill to create")
    parser.add_argument("--target-dir", type=str, default=".", help="Target directory for creation")
    parser.add_argument("--path", type=str, help="Path to existing skill for validation")
    args = parser.parse_args()

    if args.action == "create":
        if not args.name:
            print("[!] Error: --name required for create action")
            sys.exit(1)
        created = create_skill(args.name, Path(args.target_dir))
        print(f"[OK] Skill created successfully at: {created}")
        sys.exit(0)
    elif args.action == "validate":
        target = Path(args.path) if args.path else Path.cwd()
        report = validate_skill(target)
        print("=" * 70)
        print("ANTIGRAVITY SKILL VALIDATION AUDIT (SK-03)")
        print("=" * 70)
        print(f"Directory     : {report.get('skill_dir')}")
        print(f"Has Name      : {report.get('has_name')} (Valid slug: {report.get('name_valid')})")
        print(f"Has Desc      : {report.get('has_description')}")
        print(f"Body Lines    : {report.get('body_lines')} (Excessive: {report.get('body_too_long')})")
        print(f"Has Scripts   : {report.get('has_scripts')}")
        print(f"Has References: {report.get('has_references')}")
        print("=" * 70)
        print(f"STATUS        : {'PASS' if report.get('valid') else 'FAIL'}")
        print("=" * 70)
        sys.exit(0 if report.get("valid") else 1)

if __name__ == "__main__":
    main()
