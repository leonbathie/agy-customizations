#!/usr/bin/env python3
"""
SK-03 Migration Engine: migrator.py
Converts legacy AI assistant configurations into native Google Antigravity customizations:
- .cursorrules (Cursor) -> GEMINI.md / AGENTS.md + skills/
- CLAUDE.md / .clauderc (Claude Code) -> AGENTS.md + skills/
- .windsurfrules (Windsurf) -> GEMINI.md
- Copilot instructions (.github/copilot-instructions.md) -> GEMINI.md
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple

SOURCE_CANDIDATES = [
    (".cursorrules", "cursor"),
    ("CLAUDE.md", "claude"),
    (".clauderc", "claude_json"),
    (".windsurfrules", "windsurf"),
    (".github/copilot-instructions.md", "copilot")
]

def detect_legacy_configs(search_dir: Path) -> List[Tuple[Path, str]]:
    found = []
    for rel_path, kind in SOURCE_CANDIDATES:
        p = search_dir / rel_path
        if p.is_file():
            found.append((p, kind))
    return found

def convert_rule_to_antigravity(source_path: Path, kind: str, output_dir: Path) -> Dict[str, Any]:
    raw = source_path.read_text(encoding="utf-8", errors="replace")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Strip any existing YAML frontmatter if migrating to GEMINI.md / AGENTS.md
    cleaned = re.sub(r'^---\s*\n.*?\n---\s*\n', '', raw, flags=re.DOTALL).strip()
    
    # 2. Extract potential procedural instructions into skills
    # Look for code blocks or workflows with steps (e.g. 1. 2. 3.)
    workflow_matches = re.findall(r'(###?\s+(?:Workflow|Procédure|Runbook|Guide|Pipeline|Steps).*?)(?=\n###? |\Z)', cleaned, flags=re.DOTALL | re.IGNORECASE)
    
    extracted_skills = []
    if workflow_matches:
        for idx, wf in enumerate(workflow_matches, 1):
            title_line = wf.split('\n')[0].strip('# \t\r')
            skill_slug = re.sub(r'[^a-z0-9]+', '-', title_line.lower()).strip('-') or f"migrated-workflow-{idx}"
            skill_target = output_dir / ".agents" / "skills" / skill_slug
            skill_target.mkdir(parents=True, exist_ok=True)
            
            skill_md = f"""---
name: {skill_slug}
description: >-
  Compétence migrée depuis {kind} ({source_path.name}) pour : {title_line}.
---

# {title_line}

{wf}
"""
            (skill_target / "SKILL.md").write_text(skill_md, encoding="utf-8")
            extracted_skills.append(skill_slug)
            
    # 3. Create target GEMINI.md
    header = f"""# DIRECTIVES D'INGÉNIERIE LOGICIELLE (MIGRÉ DE {kind.upper()})
<!-- Source originale : {source_path.name} -->
<!-- Conforme aux spécifications Antigravity v2.0 (sans frontmatter YAML) -->

"""
    gemini_path = output_dir / "GEMINI.md"
    gemini_path.write_text(header + cleaned + "\n", encoding="utf-8")
    
    return {
        "source": str(source_path),
        "kind": kind,
        "target_rules": str(gemini_path),
        "extracted_skills": extracted_skills,
        "bytes_migrated": len(cleaned)
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Migrate Cursor/Claude/Windsurf to Antigravity")
    parser.add_argument("--source-dir", default=".", help="Source project folder")
    parser.add_argument("--dest-dir", default=".", help="Destination folder")
    args = parser.parse_args()

    src = Path(args.source_dir).resolve()
    dst = Path(args.dest_dir).resolve()
    configs = detect_legacy_configs(src)

    if not configs:
        print(f"[!] Aucune configuration legacy détectée dans {src}.")
        sys.exit(0)

    for cfg_path, kind in configs:
        res = convert_rule_to_antigravity(cfg_path, kind, dst)
        print(f"[✓] Migration réussie ({res['kind']}) : {cfg_path.name} -> {res['target_rules']}")
        if res['extracted_skills']:
            print(f"    Skills extraits : {', '.join(res['extracted_skills'])}")
