---
name: sk-04-plugin-packaging
description: >-
  Sous-skill SK-04 : Empaquetage, validation de manifeste et distribution de plugins Antigravity.
  À activer pour créer ou auditer un plugin (plugin.json), vérifier l'emplacement strict de hooks.json
  à la racine, gérer les espaces de noms, et configurer l'activation/désactivation via config.json.
---

# SK-04 — Plugin Packaging & Manifest Engineering

Ce sous-skill régit la création et la distribution de **Plugins Antigravity**, les unités tout-en-un partageables regroupant compétences, règles, serveurs MCP et intercepteurs de cycle de vie.

---

## 1. Arborescence Standard d'un Plugin Natif

Tout plugin natif doit se situer dans un dossier dédié sous un répertoire `plugins/` :

```text
plugins/<plugin_name>/
├── plugin.json       # OBLIGATOIRE : Manifeste déclaratif
├── hooks.json        # OPTIONNEL : Intercepteurs (STRICTEMENT à la racine du plugin)
├── mcp_config.json   # OPTIONNEL : Définition des serveurs MCP embarqués
├── rules/            # OPTIONNEL : Règles consolidées (AGENTS.md recommandé)
│   └── AGENTS.md
└── skills/           # OPTIONNEL : Compétences embarquées
    └── <skill_name>/
        └── SKILL.md
```

> [!IMPORTANT]
> Pour les plugins natifs, le fichier `hooks.json` doit impérativement se trouver à la racine du répertoire du plugin (`<plugin_dir>/hooks.json`). Ne jamais l'imbriquer dans un sous-dossier `hooks/`.

---

## 2. Spécification du Manifeste (`plugin.json`)

Le fichier `plugin.json` déclare l'identité et les métadonnées du paquet :

```json
{
  "name": "full-stack-toolkit",
  "author": {
    "name": "Platform Engineering Team",
    "url": "https://company.internal/team"
  },
  "homepage": "https://company.internal/plugins/toolkit",
  "repository": {
    "type": "git",
    "url": "https://github.com/company/full-stack-toolkit.git"
  },
  "disabled": false
}
```

---

## 3. Gestion d'État et Précédence d'Activation

1. **Par défaut :** Tout plugin découvert est **activé par défaut**, sauf si `"disabled": true` est stipulé dans son `plugin.json`.
2. **Priorité Utilisateur (`config.json`) :**
   Le choix de l'utilisateur est consigné dans `~/.gemini/config/config.json` :
   ```json
   {
     "plugins": {
       "full-stack-toolkit": { "enabled": false }
     }
   }
   ```
   L'entrée dans `config.json` l'emporte toujours sur le manifeste du plugin.

---

## 4. Outil d'Empaquetage et de Contrôle

Le script `bundle_plugin.py` vérifie l'intégrité structurelle et fabrique l'archive de déploiement :

```powershell
python ./scripts/bundle_plugin.py --plugin-dir "C:\mon\plugin" --output-archive "./dist"
```
