# Cycle de Vie et Interception Événementielle (SK-05)

Ce document formalise les points d'interception dans la boucle d'exécution de l'agent Antigravity.

---

## 1. Séquence Temporelle de la Boucle d'Exécution

```text
[Démarrage Session] ────► SessionStart (Initialisation de l'environnement)
      │
      ▼
[Préparation Modèle] ───► PreInvocation (Injection de contexte / rappels)
      │
      ▼
  [Appel LLM]
      │
      ├──────────────────► [Si Tool Call émis]
      │                          │
      │                          ▼
      │                     PreToolUse (Garde de sécurité / validation d'arguments)
      │                          │
      │                          ▼
      │                    [Exécution Outil]
      │                          │
      │                          ▼
      │                     PostToolUse (Linting, formattage, audit diff)
      │                          │
      │                          ▼
      ▼                     PostInvocation (Synthèse des retours outils)
[Fin de Tournée]
      │
      ▼
[Arrêt Session] ────────► Stop (Nettoyage des conteneurs / télémétrie finale)
```

---

## 2. Distinction Critique des Structures JSON

- **Structure Groupée (`PreToolUse`, `PostToolUse`) :**
  Nécessite impérativement le bloc d'encapsulation avec `matcher` et le tableau `hooks` pour cibler précisément un outil spécifique (ex: `run_command` vs `write_file`).
- **Structure Plate (`SessionStart`, `PreInvocation`, etc.) :**
  Prend directement un tableau d'objets commandes, sans niveau intermédiaire de `matcher`.
