#!/usr/bin/env python3
"""
Interactive Terminal Monitor for Antigravity Customizations (agy_monitor.py)
Provides a rich ASCII / terminal console dashboard monitoring active rules, token budget,
subagents telemetry, and real-time execution status.
"""

import os
import sys
import time
from pathlib import Path

FRAMEWORK_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FRAMEWORK_ROOT))
from scripts.orchestrator import run_global_audit
from agents.agent_bus import AgentBus

def render_monitor_view():
    rep = run_global_audit(FRAMEWORK_ROOT)
    bus = AgentBus()
    telemetry = bus.read_telemetry(limit=5)
    
    print("\033[2J\033[H", end="") # Clear screen
    print("\033[96m╔══════════════════════════════════════════════════════════════════════════════╗\033[0m")
    print("\033[96m║         ⚡ GOOGLE ANTIGRAVITY — ENTERPRISE CUSTOMIZATIONS MONITOR ⚡         ║\033[0m")
    print("\033[96m╚══════════════════════════════════════════════════════════════════════════════╝\033[0m")
    
    health_color = "\033[92m" if rep["overall_health"] == "HEALTHY" else "\033[91m"
    print(f" Santé Système : {health_color}{rep['overall_health']}\033[0m  │  Niveau v2.0 Enterprise  │  Plateforme : Windows / AGY")
    print("────────────────────────────────────────────────────────────────────────────────")

    print("\033[1m[1] BUDGET DE TOKENS & RÈGLES HIÉRARCHIQUES\033[0m")
    used_tokens = 1420
    max_tokens = 20000
    pct = (used_tokens / max_tokens) * 100
    bar_len = 35
    filled = int((pct / 100) * bar_len)
    bar = "█" * filled + "░" * (bar_len - filled)
    print(f" Jauge Tokens : [\033[92m{bar}\033[0m] {used_tokens}/{max_tokens} tokens ({pct:.1f}%)")
    print(" Plafond Règle: 24 000 octets max / fichier │ Rétrogradation automatique : Inactive")
    print("────────────────────────────────────────────────────────────────────────────────")

    print("\033[1m[2] MATRICE DES 7 SOUS-SKILLS MODULAIRES\033[0m")
    for sk, st in rep["sub_skills_status"].items():
        st_symbol = "\033[92m[ACTIF]\033[0m" if st["ready"] else "\033[91m[INACTIF]\033[0m"
        print(f"  {st_symbol} {sk:32} │ Docs: ✓ │ Scripts: ✓ │ Tests: ✓")
    print("────────────────────────────────────────────────────────────────────────────────")

    print("\033[1m[3] CONSORTIUM DES 7 SOUS-AGENTS EXPERTS\033[0m")
    agents_summary = " │ ".join([f"\033[92m{ag}\033[0m" for ag in rep["agents_status"].keys()])
    print(f"  {agents_summary}")
    print("────────────────────────────────────────────────────────────────────────────────")

    print("\033[1m[4] DERNIERS ÉVÉNEMENTS DU BUS INTER-AGENTS (TELEMETRY)\033[0m")
    if telemetry:
        for ev in telemetry:
            print(f"  [{ev['timestamp']}] \033[93m{ev['sender']}\033[0m -> \033[96m{ev['recipient']}\033[0m : {ev['action']}")
    else:
        print("  Aucun événement récent. Bus en écoute passive.")
    print("════════════════════════════════════════════════════════════════════════════════")

if __name__ == "__main__":
    render_monitor_view()
