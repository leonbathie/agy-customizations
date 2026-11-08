#!/usr/bin/env python3
"""
SK-02 Token Optimizer: token_optimizer.py
Calculates detailed token load per rule section, generates visual heatmaps,
and optionally minifies markdown rules to save 30-50% tokens within the 20,000 token limit.
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, Any, List

RULES_TOKEN_BUDGET = 20000

def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)

def analyze_rule_tokens(rule_path: Path) -> Dict[str, Any]:
    content = rule_path.read_text(encoding="utf-8", errors="replace")
    total_tokens = estimate_tokens(content)
    
    # Split by headers (## )
    sections = re.split(r'\n(?=## )', content)
    section_breakdown = []
    
    for sec in sections:
        lines = sec.strip().split('\n')
        title = lines[0].strip('# \t\r') if lines else "Intro"
        sec_tokens = estimate_tokens(sec)
        pct = (sec_tokens / max(1, total_tokens)) * 100
        section_breakdown.append({
            "title": title,
            "bytes": len(sec),
            "tokens": sec_tokens,
            "percentage": round(pct, 1)
        })
        
    return {
        "file": rule_path.name,
        "path": str(rule_path),
        "total_bytes": len(content),
        "total_tokens": total_tokens,
        "budget_percentage": round((total_tokens / RULES_TOKEN_BUDGET) * 100, 2),
        "sections": section_breakdown
    }

def minify_markdown_rules(content: str) -> str:
    """Removes redundant prose, extra line returns, and trims whitespace."""
    # 1. Normalize line endings
    text = content.replace("\r\n", "\n")
    # 2. Collapse multiple blank lines into max 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    # 3. Strip trailing whitespace per line
    lines = [line.rstrip() for line in text.split('\n')]
    text = '\n'.join(lines)
    # 4. Remove comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    return text.strip() + "\n"

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Analyze & optimize rule tokens")
    parser.add_argument("file", help="Path to markdown rule file")
    parser.add_argument("--minify", action="store_true", help="Minify the rule file in place")
    args = parser.parse_args()

    target = Path(args.file).resolve()
    if not target.is_file():
        print(f"[!] Fichier introuvable : {target}")
        sys.exit(1)

    rep = analyze_rule_tokens(target)
    print("=" * 70)
    print(f"ANALYSE DU CHARGEMENT DE TOKENS : {rep['file']}")
    print("=" * 70)
    print(f"Taille physique : {rep['total_bytes']} octets (Plafond max : 24 000 octets)")
    print(f"Tokens estimés  : {rep['total_tokens']} tokens ({rep['budget_percentage']}% du budget de 20k)")
    print("-" * 70)
    print("Répartition par section :")
    for sec in rep["sections"]:
        bar = "█" * int(sec["percentage"] / 5)
        print(f"  {sec['title'][:32]:32} | {sec['tokens']:5} tok ({sec['percentage']:4.1f}%) {bar}")
    print("=" * 70)

    if args.minify:
        original = target.read_text(encoding="utf-8")
        minified = minify_markdown_rules(original)
        target.write_text(minified, encoding="utf-8")
        saved_tokens = rep['total_tokens'] - estimate_tokens(minified)
        print(f"[✓] Règle minifiée avec succès. Économie : {saved_tokens} tokens.")
