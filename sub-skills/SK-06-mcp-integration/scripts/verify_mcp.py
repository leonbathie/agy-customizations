#!/usr/bin/env python3
"""
SK-06 Helper Script: verify_mcp.py
Auditeur et vérificateur de configurations MCP (Model Context Protocol) Antigravity :
- Validation du schéma mcp_config.json
- Contrôle des transports Stdio (commande, arguments, variables d'environnement)
- Contrôle des transports Streamable HTTP (spécification 2025-03-26)
- Détection des configurations obsolètes (legacy SSE)
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from typing import Dict, Any, List

def audit_mcp_config(config_path: Path, check_binaries: bool = False) -> Dict[str, Any]:
    issues: List[str] = []
    warnings: List[str] = []
    
    if not config_path.is_file():
        return {"valid": False, "issues": [f"Fichier {config_path} introuvable."], "warnings": []}
        
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"valid": False, "issues": [f"Erreur de parsing JSON dans {config_path.name}: {e}"], "warnings": []}
        
    if not isinstance(data, dict) or "mcpServers" not in data:
        return {"valid": False, "issues": ["La clé racine 'mcpServers' est obligatoire dans mcp_config.json."], "warnings": []}

    servers = data["mcpServers"]
    if not isinstance(servers, dict):
        return {"valid": False, "issues": ["'mcpServers' doit être un objet JSON."], "warnings": []}

    server_details = {}

    for srv_name, srv_conf in servers.items():
        if not isinstance(srv_conf, dict):
            issues.append(f"Le serveur '{srv_name}' doit être configuré sous forme d'objet.")
            continue
            
        has_command = "command" in srv_conf
        has_url = "url" in srv_conf or "serverUrl" in srv_conf
        
        if not has_command and not has_url:
            issues.append(f"Le serveur '{srv_name}' doit définir soit 'command' (Stdio), soit 'url' (Streamable HTTP).")
            continue
            
        if has_command and has_url:
            issues.append(f"Le serveur '{srv_name}' ne peut pas mélanger 'command' et 'url' simultanément.")
            continue

        transport = "stdio" if has_command else "streamable_http"
        binary_found = True

        if transport == "stdio":
            cmd = srv_conf["command"]
            if not isinstance(cmd, str) or not cmd.strip():
                issues.append(f"Le serveur '{srv_name}' a une commande invalide.")
            elif check_binaries:
                resolved_bin = shutil.which(cmd)
                if not resolved_bin and not Path(cmd).exists():
                    warnings.append(f"Binaire introuvable sur le PATH pour '{srv_name}': {cmd}")
                    binary_found = False

            args = srv_conf.get("args", [])
            if not isinstance(args, list):
                issues.append(f"Les 'args' du serveur '{srv_name}' doivent être une liste de chaînes.")

            env = srv_conf.get("env", {})
            if not isinstance(env, dict):
                issues.append(f"L''env' du serveur '{srv_name}' doit être un objet dictionnaire.")
                
        elif transport == "streamable_http":
            url = srv_conf.get("url") or srv_conf.get("serverUrl", "")
            if not url.startswith("http://") and not url.startswith("https://"):
                issues.append(f"L'URL du serveur '{srv_name}' doit débuter par http:// ou https://.")
            if "/sse" in url:
                warnings.append(f"Le serveur '{srv_name}' semble pointer vers un endpoint legacy /sse. Streamable HTTP (/mcp) est requis.")

        server_details[srv_name] = {
            "transport": transport,
            "binary_found": binary_found
        }

    is_valid = len(issues) == 0
    return {
        "valid": is_valid,
        "servers_count": len(server_details),
        "servers": server_details,
        "issues": issues,
        "warnings": warnings
    }

def main():
    parser = argparse.ArgumentParser(description="Antigravity MCP Configuration Verifier")
    parser.add_argument("--config", type=str, default="mcp_config.json", help="Path to mcp_config.json")
    parser.add_argument("--test-transports", action="store_true", help="Check if binaries are on PATH")
    args = parser.parse_args()

    cfg_path = Path(args.config).resolve()
    report = audit_mcp_config(cfg_path, args.test_transports)

    print("=" * 70)
    print("ANTIGRAVITY MCP CONFIGURATION AUDIT (SK-06)")
    print("=" * 70)
    print(f"File Path        : {cfg_path}")
    print(f"Servers Defined  : {report.get('servers_count')}")
    for srv_name, det in report.get("servers", {}).items():
        print(f" -> [{srv_name}] Transport: {det['transport']} (Binary OK: {det['binary_found']})")
    print("-" * 70)

    for issue in report.get("issues", []):
        print(f"[!] ERROR: {issue}")
    for warning in report.get("warnings", []):
        print(f"[!] WARN : {warning}")

    print("=" * 70)
    print(f"STATUS           : {'PASS' if report['valid'] else 'FAIL'}")
    print("=" * 70)

    sys.exit(0 if report['valid'] else 1)

if __name__ == "__main__":
    main()
