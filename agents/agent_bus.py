#!/usr/bin/env python3
"""
Inter-Agent Communication Bus for Antigravity Consortium
Handles dispatching, handoffs, message queuing, and telemetric logging across the 7 sub-agents.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

AGENTS_DIR = Path(__file__).resolve().parent
LOG_FILE = AGENTS_DIR / "agents_telemetry.jsonl"

KNOWN_AGENTS = {
    "agent-kernel": "Kernel & Discovery Architect",
    "agent-rules": "Rules Engine & Governance Lead",
    "agent-skill": "Modular Skill Author & Formatter",
    "agent-plugin": "Plugin Packaging & Bundle Specialist",
    "agent-hook": "Lifecycle Hook & Event Interceptor",
    "agent-mcp": "MCP Integration & Sandbox Engineer",
    "agent-deployer": "CI/CD & Deployment Validator"
}

class AgentBus:
    def __init__(self, log_path: Path = LOG_FILE):
        self.log_path = log_path

    def dispatch(self, sender: str, recipient: str, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if sender not in KNOWN_AGENTS:
            raise ValueError(f"Expéditeur inconnu : '{sender}'")
        if recipient not in KNOWN_AGENTS and recipient != "all":
            raise ValueError(f"Destinataire inconnu : '{recipient}'")

        event = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "sender": sender,
            "sender_role": KNOWN_AGENTS[sender],
            "recipient": recipient,
            "action": action,
            "payload": payload,
            "status": "DELIVERED"
        }

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

        return event

    def read_telemetry(self, limit: int = 10) -> List[Dict[str, Any]]:
        if not self.log_path.exists():
            return []
        events = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        events.append(json.loads(line.strip()))
                    except Exception:
                        pass
        return events[-limit:]

if __name__ == "__main__":
    bus = AgentBus()
    # Test handoff from agent-kernel to agent-rules
    res = bus.dispatch(
        sender="agent-kernel",
        recipient="agent-rules",
        action="HANDOFF_WORKSPACE_RULES",
        payload={"workspace_root": "C:/Projects/demo", "rules_found": ["GEMINI.md"]}
    )
    print(f"[OK] Événement distribué avec succès : {res['action']} ({res['sender']} -> {res['recipient']})")
