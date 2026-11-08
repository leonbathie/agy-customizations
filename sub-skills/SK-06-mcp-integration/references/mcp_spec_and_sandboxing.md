# Spécification et Sandboxing MCP (SK-06)

Ce document décrit le fonctionnement des intégrations MCP sous Antigravity.

---

## 1. Modèle de Sécurité et Sandboxing

Tout serveur MCP exécuté localement en mode **Stdio** hérite des privilèges restreints de l'environnement :
1. **Variables d'Environnement Déclaratives :** Les secrets doivent être injectés via le bloc `env` de `mcp_config.json`, sans exposition dans l'historique du terminal.
2. **Isolation des Processus :** Le sous-processus est attaché au cycle de vie du serveur de langage Antigravity. À l'arrêt de la session, tous les processus fils sont terminés proprement.

---

## 2. Standardisation HTTP 2025-03-26

Pour les serveurs distants, Antigravity applique la norme **Streamable HTTP** :
- Le serveur écoute sur une route dédiée (couramment `/mcp`).
- La communication utilise des flux chunked HTTP/2 ou HTTP/1.1 bidirectionnels.
- L'authentification est gérée par en-têtes standard (`Authorization: Bearer ...`).
