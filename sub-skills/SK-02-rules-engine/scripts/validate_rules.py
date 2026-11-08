#!/usr/bin/env python3
"""
SK-02 Helper Script: validate_rules.py
Valide la conformité des règles d'espace de travail Antigravity :
- Plafond de 24 000 octets par fichier
- Budget cumulé de 20 000 tokens
- Résolution des inclusions @[label](path)
- Absence de frontmatter dans GEMINI.md / AGENTS.md
"""

import os
import sys
import re
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple

MAX_BYTES_PER_RULE = 24000
DEFAULT_RULES_BUDGET_TOKENS = 20000

INCLUDE_PATTERN = re.compile(r'@\[(.*?)\]\((.*?)\)')
YAML_FRONTMATTER_PATTERN = re.compile(r'^---\s*\n.*?\n---\s*\n', re.DOTALL)

def estimate_tokens(text: str) -> int:
    # Heuristic ratio: ~4 chars per token for typical English/code
    return max(1, len(text) // 4)

def resolve_includes(file_path: Path, visited: set) -> Tuple[str, List[str]]:
    warnings = []
    if file_path in visited:
        warnings.append(f"Circularity detected for {file_path}")
        return "", warnings
    
    visited.add(file_path)
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        warnings.append(f"Cannot read file {file_path}: {e}")
        return "", warnings

    def replace_include(match):
        label = match.group(1)
        rel_path = match.group(2)
        target = (file_path.parent / rel_path).resolve()
        if not target.is_file():
            warnings.append(f"Included target not found: '{rel_path}' referenced in {file_path.name}")
            return match.group(0)
        sub_content, sub_warn = resolve_includes(target, visited.copy())
        warnings.extend(sub_warn)
        return sub_content

    expanded = INCLUDE_PATTERN.sub(replace_include, content)
    return expanded, warnings

def audit_rule_file(path: Path) -> Dict[str, Any]:
    file_bytes = path.stat().st_size
    raw_content = path.read_text(encoding="utf-8", errors="replace")
    has_yaml = bool(YAML_FRONTMATTER_PATTERN.match(raw_content))
    
    expanded_content, include_warnings = resolve_includes(path, set())
    expanded_bytes = len(expanded_content.encode("utf-8"))
    token_est = estimate_tokens(expanded_content)
    
    is_standalone_rule = path.name in ["GEMINI.md", "AGENTS.md"]
    yaml_violation = is_standalone_rule and has_yaml
    byte_violation = expanded_bytes > MAX_BYTES_PER_RULE

    return {
        "path": str(path.resolve()),
        "file_name": path.name,
        "is_standalone_rule": is_standalone_rule,
        "raw_bytes": file_bytes,
        "expanded_bytes": expanded_bytes,
        "tokens_est": token_est,
        "has_yaml_frontmatter": has_yaml,
        "yaml_violation": yaml_violation,
        "byte_violation": byte_violation,
        "warnings": include_warnings,
        "is_valid": (not yaml_violation) and (not byte_violation) and len(include_warnings) == 0
    }

def scan_and_validate_rules(target_dir: Path, max_bytes: int = MAX_BYTES_PER_RULE, budget: int = DEFAULT_RULES_BUDGET_TOKENS) -> Dict[str, Any]:
    rule_files = []
    # Find all AGENTS.md, GEMINI.md, and *.md in rules/ directories
    for p in target_dir.rglob("*.md"):
        if p.name in ["GEMINI.md", "AGENTS.md"] or "rules" in p.parts:
            rule_files.append(p)
            
    results = [audit_rule_file(rf) for rf in rule_files]
    total_tokens = sum(r["tokens_est"] for r in results)
    budget_exceeded = total_tokens > budget
    
    all_valid = all(r["is_valid"] for r in results) and not budget_exceeded

    return {
        "scanned_directory": str(target_dir.resolve()),
        "rules_found": len(results),
        "total_estimated_tokens": total_tokens,
        "token_budget": budget,
        "budget_exceeded": budget_exceeded,
        "rules": results,
        "all_valid": all_valid
    }

def main():
    parser = argparse.ArgumentParser(description="Antigravity Rules Validator")
    parser.add_argument("--path", type=str, default=".", help="Directory to scan for rule files")
    parser.add_argument("--max-bytes", type=int, default=MAX_BYTES_PER_RULE, help="Max bytes per expanded rule file")
    parser.add_argument("--budget-tokens", type=int, default=DEFAULT_RULES_BUDGET_TOKENS, help="Max aggregate token budget")
    args = parser.parse_args()

    report = scan_and_validate_rules(Path(args.path), args.max_bytes, args.budget_tokens)
    
    print("=" * 70)
    print("ANTIGRAVITY RULES ENGINE AUDIT (SK-02)")
    print("=" * 70)
    print(f"Target Directory     : {report['scanned_directory']}")
    print(f"Rules Evaluated      : {report['rules_found']}")
    print(f"Total Est. Tokens    : {report['total_estimated_tokens']} / {report['token_budget']}")
    print(f"Budget Exceeded      : {report['budget_exceeded']}")
    print("-" * 70)
    
    for r in report["rules"]:
        status = "PASS" if r["is_valid"] else "FAIL"
        print(f"[{status}] {r['file_name']} -> {r['expanded_bytes']} octets | ~{r['tokens_est']} tokens")
        if r["yaml_violation"]:
            print("       [!] VIOLATION: YAML frontmatter forbidden in standalone rule")
        if r["byte_violation"]:
            print(f"       [!] VIOLATION: File size {r['expanded_bytes']} exceeds {args.max_bytes} bytes cap")
        for w in r["warnings"]:
            print(f"       [!] WARNING: {w}")

    print("=" * 70)
    print(f"OVERALL STATUS: {'PASS' if report['all_valid'] else 'FAIL'}")
    print("=" * 70)
    
    sys.exit(0 if report['all_valid'] else 1)

if __name__ == "__main__":
    main()
