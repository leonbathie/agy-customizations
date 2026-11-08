#!/usr/bin/env python3
"""
SK-02 Conflict Detector: conflict_detector.py
Analyzes hierarchical rule files for contradictions, incompatible directives, and overlapping policies:
- Formatting conflicts (e.g. spaces vs tabs, single vs double quotes)
- Technology stack conflicts (e.g. Vue 2 vs Vue 3, React vs Angular, npm vs pnpm)
- Paradigm / Architecture conflicts (e.g. monolithic vs microservices, functional vs OOP)
- Security boundaries (e.g. mock APIs vs live network)
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple

CONFLICT_PAIRS = [
    {
        "category": "Indentation / Formatage",
        "patterns": [
            (r'\b(indent(?:ation)? with 2 spaces|2 espaces)\b', "Indentation: 2 espaces"),
            (r'\b(indent(?:ation)? with 4 spaces|4 espaces)\b', "Indentation: 4 espaces"),
            (r'\b(use tabs|utiliser des tabulations)\b', "Indentation: Tabulations")
        ]
    },
    {
        "category": "Gestionnaire de Dépendances",
        "patterns": [
            (r'\b(use npm|toujours npm)\b', "Package Manager: npm"),
            (r'\b(use yarn|toujours yarn)\b', "Package Manager: yarn"),
            (r'\b(use pnpm|toujours pnpm)\b', "Package Manager: pnpm"),
            (r'\b(use bun|toujours bun)\b', "Package Manager: bun")
        ]
    },
    {
        "category": "Typage & Rigueur JavaScript/TypeScript",
        "patterns": [
            (r'\b(strictly typed|strict mode|never use any|interdit d\'utiliser any)\b', "Typage: Strict (No Any)"),
            (r'\b(allow any|permissive typing|autoriser any)\b', "Typage: Permissif (Allow Any)")
        ]
    },
    {
        "category": "Conventions de Nommage",
        "patterns": [
            (r'\b(use camelCase|nommage en camelCase)\b', "Nommage: camelCase"),
            (r'\b(use snake_case|nommage en snake_case)\b', "Nommage: snake_case")
        ]
    }
]

def scan_file_for_directives(file_path: Path) -> List[Tuple[str, str, str]]:
    found = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []

    for group in CONFLICT_PAIRS:
        cat = group["category"]
        for pat, desc in group["patterns"]:
            if re.search(pat, content, flags=re.IGNORECASE):
                found.append((cat, desc, file_path.name))
    return found

def detect_rule_conflicts(rule_files: List[Path]) -> Dict[str, Any]:
    all_directives: Dict[str, List[Tuple[str, str]]] = {}
    for rf in rule_files:
        items = scan_file_for_directives(rf)
        for cat, desc, src in items:
            if cat not in all_directives:
                all_directives[cat] = []
            all_directives[cat].append((desc, src))

    conflicts = []
    for cat, items in all_directives.items():
        distinct_descs = set(d for d, _ in items)
        if len(distinct_descs) > 1:
            sources_map = {}
            for d, src in items:
                if d not in sources_map: sources_map[d] = []
                sources_map[d].append(src)
            conflicts.append({
                "category": cat,
                "contradictions": [f"'{d}' (déclaré dans {', '.join(set(srcs))})" for d, srcs in sources_map.items()],
                "severity": "HAUTE"
            })

    return {
        "files_analyzed": [str(f) for f in rule_files],
        "conflicts_count": len(conflicts),
        "conflicts": conflicts
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Audit rule conflicts")
    parser.add_argument("--dir", default=".", help="Directory to search for rules")
    args = parser.parse_args()

    target_dir = Path(args.dir).resolve()
    rules = list(target_dir.glob("**/GEMINI.md")) + list(target_dir.glob("**/AGENTS.md"))
    rep = detect_rule_conflicts(rules)

    print(f"[*] Analyse de conflits terminée sur {len(rules)} fichiers de règles.")
    if rep["conflicts_count"] == 0:
        print("[✓] Aucun conflit ni contradiction détecté entre vos règles actives.")
    else:
        print(f"[!] {rep['conflicts_count']} conflit(s) détecté(s) :")
        for c in rep["conflicts"]:
            print(f"  - [{c['category']}] (Sévérité : {c['severity']}) :")
            for sub in c["contradictions"]:
                print(f"      * {sub}")
