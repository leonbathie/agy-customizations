---
name: sk-05-lifecycle-hooks
description: >-
  Sous-skill SK-05 : Interception d'événements et automatisation du cycle de vie via hooks.json.
  À activer pour implémenter des gardes de sécurité (PreToolUse), des linters/formateurs (PostToolUse),
  des initialisations de session (SessionStart), ou auditer les 6 phases d'interception Antigravity.
---

# SK-05 — Lifecycle Hooks Engineering

Ce sous-skill régit la configuration, l'exécution et l'audit des **Hooks de cycle de vie (`hooks.json`)**. Les hooks permettent d'exécuter des commandes shell déterministes à des points charnières de la boucle d'exécution de l'agent.

---

## 1. Les 6 Phases d'Interception du Cycle de Vie

| Événement | Moment de déclenchement | Structure JSON | Cible du Matcher |
| :--- | :--- | :--- | :--- |
| **`SessionStart`** | Initialisation d'une nouvelle session | Liste plate | Non applicable |
| **`PreToolUse`** | Immédiatement avant l'appel d'un outil | Groupée (`matcher` + `hooks`) | Nom de l'outil (`run_command`, etc.) |
| **`PostToolUse`** | Immédiatement après la fin d'un outil | Groupée (`matcher` + `hooks`) | Nom de l'outil |
| **`PreInvocation`** | Avant la transmission du prompt au modèle | Liste plate | Non applicable |
| **`PostInvocation`** | Après l'exécution de la réponse du modèle | Liste plate | Non applicable |
| **`Stop`** | À la terminaison de la boucle d'exécution | Liste plate | Non applicable |

---

## 2. Structure Canonique de `hooks.json`

Le fichier est composé d'objets nommés permettant la fusion ordonnée de plusieurs configurations :

```json
{
  "security-sentinel": {
    "enabled": true,
    "PreToolUse": [
      {
        "matcher": "run_command",
        "hooks": [
          {
            "type": "command",
            "command": "./scripts/guard_command.py",
            "timeout": 5
          }
        ]
      }
    ]
  },
  "code-hygiene": {
    "PostToolUse": [
      {
        "matcher": "write_file",
        "hooks": [
          {
            "type": "command",
            "command": "./scripts/auto_format.py",
            "timeout": 15
          }
        ]
      }
    ]
  },
  "session-init": {
    "SessionStart": [
      {
        "type": "command",
        "command": "./scripts/bootstrap_env.sh"
      }
    ]
  }
}
```

---

## 3. Règles d'Exécution et Contrat de Sortie

1. **Code de Sortie 0 (Succès) :** Le flux d'exécution standard se poursuit normalement.
2. **Code de Sortie Non-Nul (Échec / Blocage) :**
   - En phase `PreToolUse`, un code non-nul **bloque immédiatement** l'exécution de l'outil et retourne l'erreur standard (`stderr`) au modèle.
   - En phase `SessionStart` ou `PostToolUse`, un code non-nul remonte un avertissement dans la télémétrie.
3. **Timeout Stricte :** Tout hook dépassant son paramètre `timeout` (en secondes) est tué via `SIGKILL`.

---

## 4. Outil de Simulation et d'Audit

Le script `hook_runner.py` permet de valider la syntaxe et simuler le déclenchement d'un événement :

```powershell
# Validation syntaxique
python ./scripts/hook_runner.py --file "./hooks.json" --validate

# Simulation d'un événement PreToolUse pour run_command
python ./scripts/hook_runner.py --file "./hooks.json" --trigger PreToolUse --tool run_command
```
