---
name: sk-07-deployment-validation
description: >-
  Sous-skill SK-07 : Déploiement multi-environnements, configurations déclaratives (skills.json, plugins.json),
  et validation CI/CD de bout en bout. À activer pour auditer les manifestes d'héritage, valider la résolution
  des chemins (absolus, home ~, relatifs workspace) et exécuter la chaîne de vérification télémetrique.
---

# SK-07 — Deployment, Manifests & CI/CD Validation

Ce sous-skill régit la distribution à l'échelle d'une équipe, l'héritage de configurations partagées (`skills.json`, `plugins.json`) et l'automatisation des tests de régression en intégration continue (CI/CD).

---

## 1. Schéma des Fichiers de Configuration Déclaratifs

Placés dans le dossier de personnalisation racine (ex: `.agents/skills.json` ou `.agents/plugins.json`) :

```json
{
  "inherits": [
    {
      "path": "/shared/team-configs/skills.json",
      "include_only": ["linter-*", "security-*"],
      "exclude": ["*-deprecated"]
    }
  ],
  "entries": [
    {
      "path": "./custom-skills",
      "exclude": ["experimental-.*"]
    },
    {
      "path": "~/personal-tools/skills"
    }
  ]
}
```

---

## 2. Règles de Résolution des Chemins (`path`)

1. **Chemins Absolus (`/` ou `C:\`) :** Résolus directement sur le système de fichiers hôte.
2. **Chemins Relatifs au Répertoire Utilisateur (`~/`) :** Résolus par rapport au dossier personnel de l'utilisateur (`$HOME` ou `%USERPROFILE%`).
3. **Chemins Relatifs à l'Espace de Travail :** Tout chemin ne débutant ni par `/` ni par `~` est résolu par rapport à la racine du dépôt de code (le dossier contenant `.git`).

---

## 3. Chaîne d'Intégration et Validation CI/CD

Avant tout commit dans un dépôt d'équipe, le pipeline CI/CD exécute les vérifications fondamentales :
- **Validité des schémas JSON :** `plugin.json`, `hooks.json`, `mcp_config.json`, `skills.json`.
- **Budgets de règles :** Absence de fichiers `AGENTS.md` excédant 24 000 octets.
- **Divulgation progressive :** Tous les `SKILL.md` possèdent un frontmatter YAML valide.
- **Emplacement des hooks :** Aucun `hooks.json` égaré dans un sous-dossier non conforme.

---

## 4. Outil de Déploiement et d'Audit CI

Le script `ci_deploy_validator.py` exécute la suite complète de contrôles :

```powershell
python ./scripts/ci_deploy_validator.py --workspace-root "." --strict-ci
```
