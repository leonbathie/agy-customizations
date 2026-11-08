---
name: sk-06-mcp-integration
description: >-
  Sous-skill SK-06 : Configuration, sécurité et validation des serveurs Model Context Protocol (MCP).
  À activer pour orchestrer mcp_config.json, intégrer des transports Stdio locaux ou Streamable HTTP
  (spécification 2025-03-26), configurer le sandboxing d'environnement et auditer les outils injectés.
---

# SK-06 — MCP Server Integration & Protocols

Ce sous-skill régit la configuration, le diagnostic et la sécurisation des connexions **Model Context Protocol (MCP)** dans Antigravity.

---

## 1. Emplacements de Configuration (`mcp_config.json`)

1. **Configuration Globale :** `~/.gemini/config/mcp_config.json` (actif pour l'ensemble des sessions de la machine).
2. **Configuration Embarquée dans un Plugin :** `plugins/<nom>/mcp_config.json` (activé uniquement lorsque le plugin est actif).

---

## 2. Transports Pris en Charge

Antigravity prend en charge deux mécanismes de transport standardisés :

### A. Transport Stdio (Exécution Locale)
Utilisé pour exécuter un sous-processus local communiquant sur les flux d'entrée/sortie standard (`stdin`/`stdout`) :

```json
{
  "mcpServers": {
    "git-analyzer": {
      "command": "python",
      "args": ["-m", "git_mcp_server", "--readonly"],
      "env": {
        "GIT_PYTHON_REFRESH": "quiet"
      }
    }
  }
}
```

### B. Transport Streamable HTTP (Services Distants)
Conforme à la spécification MCP du 26 mars 2025 :

```json
{
  "mcpServers": {
    "cloud-knowledge": {
      "url": "https://mcp.internal.company.com/mcp"
    }
  }
}
```

> [!WARNING]
> Le protocole legacy HTTP+SSE (spécification 2024-11-05) n'est pas supporté nativement. Pour connecter un serveur legacy SSE, utilisez un pont Stdio tel que `mcp-remote` en mode Stdio.

---

## 3. Découverte et Injection d'Outils

1. **Interrogation du serveur :** Antigravity initialise la session et invoque `tools/list`.
2. **Injection dans le Prompt :** Chaque outil découvert est encapsulé avec ses schémas d'arguments JSON Schema et mis à disposition de l'agent.
3. **Isolation :** Pour les serveurs hébergés dans des plugins, les outils sont automatiquement préfixés par l'espace de noms du plugin pour prévenir toute collision.

---

## 4. Outil de Vérification Exécutable

Le script `verify_mcp.py` permet d'auditer et tester la validité des configurations MCP :

```powershell
python ./scripts/verify_mcp.py --config "./mcp_config.json" --test-transports
```
