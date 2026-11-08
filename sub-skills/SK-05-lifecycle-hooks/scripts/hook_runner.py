#!/usr/bin/env python3
"""
SK-05 Helper Script: hook_runner.py
Auditeur et simulateur pour les hooks de cycle de vie Antigravity (hooks.json) :
- Validation syntaxique et structurelle des 6 phases d'interception
- Vérification des structures plates vs groupées (matcher + hooks)
- Simulation déterministe de déclenchement d'événements
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List

FLAT_EVENTS = {"SessionStart", "PreInvocation", "PostInvocation", "Stop"}
GROUPED_EVENTS = {"PreToolUse", "PostToolUse"}
ALL_EVENTS = FLAT_EVENTS | GROUPED_EVENTS

def validate_hooks_file(file_path: Path) -> Dict[str, Any]:
    issues: List[str] = []
    warnings: List[str] = []
    
    if not file_path.is_file():
        return {"valid": False, "issues": [f"Fichier {file_path} introuvable."], "warnings": []}
        
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"valid": False, "issues": [f"JSON invalide dans {file_path.name}: {e}"], "warnings": []}
        
    if not isinstance(data, dict):
        return {"valid": False, "issues": ["Le fichier hooks.json doit contenir un objet racine."], "warnings": []}

    total_hooks_count = 0

    for hook_name, hook_spec in data.items():
        if not isinstance(hook_spec, dict):
            issues.append(f"La section '{hook_name}' doit être un objet JSON.")
            continue
            
        enabled = hook_spec.get("enabled", True)
        
        for event_key, handlers in hook_spec.items():
            if event_key == "enabled":
                continue
            if event_key not in ALL_EVENTS:
                warnings.append(f"Événement inconnu '{event_key}' dans le hook '{hook_name}'.")
                continue
                
            if not isinstance(handlers, list):
                issues.append(f"L'événement '{event_key}' dans '{hook_name}' doit être une liste.")
                continue

            total_hooks_count += len(handlers)

            if event_key in GROUPED_EVENTS:
                # Must be grouped with matcher and hooks list
                for idx, entry in enumerate(handlers):
                    if not isinstance(entry, dict):
                        issues.append(f"{event_key}[{idx}] dans '{hook_name}' doit être un objet.")
                        continue
                    if "matcher" not in entry:
                        issues.append(f"{event_key}[{idx}] dans '{hook_name}' requiert le champ 'matcher'.")
                    if "hooks" not in entry or not isinstance(entry["hooks"], list):
                        issues.append(f"{event_key}[{idx}] dans '{hook_name}' requiert une liste 'hooks'.")
                    else:
                        for h_idx, h in enumerate(entry["hooks"]):
                            if "command" not in h:
                                issues.append(f"{event_key}[{idx}].hooks[{h_idx}] requiert 'command'.")
            elif event_key in FLAT_EVENTS:
                # Flat list of handler objects
                for idx, handler in enumerate(handlers):
                    if not isinstance(handler, dict):
                        issues.append(f"{event_key}[{idx}] dans '{hook_name}' doit être un objet direct.")
                    elif "command" not in handler:
                        issues.append(f"{event_key}[{idx}] dans '{hook_name}' requiert 'command'.")

    return {
        "valid": len(issues) == 0,
        "total_hooks_count": total_hooks_count,
        "named_hooks": list(data.keys()),
        "issues": issues,
        "warnings": warnings,
        "data": data
    }

def simulate_trigger(file_path: Path, event: str, tool_name: str = "") -> List[Dict[str, Any]]:
    audit = validate_hooks_file(file_path)
    if not audit["valid"]:
        raise ValueError(f"Fichier hooks invalide : {'; '.join(audit['issues'])}")
        
    triggered = []
    data = audit["data"]
    
    for hook_name, hook_spec in data.items():
        if not hook_spec.get("enabled", True):
            continue
        if event not in hook_spec:
            continue
            
        handlers = hook_spec[event]
        if event in GROUPED_EVENTS:
            for group in handlers:
                matcher = group.get("matcher", "")
                if matcher == tool_name or matcher == "*" or not tool_name:
                    for h in group.get("hooks", []):
                        triggered.append({
                            "hook_name": hook_name,
                            "event": event,
                            "matcher": matcher,
                            "matched_tool": tool_name,
                            "command": h.get("command"),
                            "timeout": h.get("timeout", 30)
                        })
        elif event in FLAT_EVENTS:
            for h in handlers:
                triggered.append({
                    "hook_name": hook_name,
                    "event": event,
                    "command": h.get("command"),
                    "timeout": h.get("timeout", 30)
                })
                
    return triggered

def main():
    parser = argparse.ArgumentParser(description="Antigravity Lifecycle Hook Auditor")
    parser.add_argument("--file", type=str, default="hooks.json", help="Path to hooks.json")
    parser.add_argument("--validate", action="store_true", help="Validate schema and structure")
    parser.add_argument("--trigger", choices=list(ALL_EVENTS), help="Simulate an event trigger")
    parser.add_argument("--tool", type=str, default="", help="Tool name for grouped event trigger")
    args = parser.parse_args()

    hook_path = Path(args.file).resolve()
    audit = validate_hooks_file(hook_path)

    print("=" * 70)
    print("ANTIGRAVITY LIFECYCLE HOOKS AUDIT (SK-05)")
    print("=" * 70)
    print(f"File Path        : {hook_path}")
    print(f"Named Hooks      : {audit.get('named_hooks')}")
    print(f"Total Handlers   : {audit.get('total_hooks_count')}")
    print("-" * 70)

    for issue in audit.get("issues", []):
        print(f"[!] ERROR: {issue}")
    for warning in audit.get("warnings", []):
        print(f"[!] WARN : {warning}")

    print("=" * 70)
    print(f"STATUS           : {'PASS' if audit['valid'] else 'FAIL'}")
    print("=" * 70)

    if args.trigger and audit["valid"]:
        matched = simulate_trigger(hook_path, args.trigger, args.tool)
        print(f"\n[SIMULATION] Triggering '{args.trigger}' (Tool: '{args.tool}'):")
        print(f"Handlers invoked : {len(matched)}")
        for m in matched:
            print(f" -> [{m['hook_name']}] Cmd: {m['command']} (Timeout: {m['timeout']}s)")

    sys.exit(0 if audit["valid"] else 1)

if __name__ == "__main__":
    main()
