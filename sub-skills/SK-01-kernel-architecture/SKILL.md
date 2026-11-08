---
name: sk-01-kernel-architecture
description: >-
  Sous-skill SK-01 : Analyse, résolution et audit du noyau de découverte et de précédence
  d'Antigravity. À activer pour valider la chaîne de recherche hiérarchique (.agents/),
  l'ordre de précédence sur 5 niveaux, la déduplication et l'allocation du budget contextuel.
---

# SK-01 — Kernel Architecture & Discovery Engine

Ce sous-skill gère le fonctionnement interne du noyau de personnalisation d'Antigravity. Il garantit que les répertoires, manifestes et fichiers de configuration sont découverts dans le strict respect de la hiérarchie du système.

---

## 1. Mécanisme de Découverte Hiérarchique

Antigravity traverse l'arborescence des répertoires depuis le répertoire de travail actuel (`CWD`) jusqu'à la racine du dépôt de code (marquée par `.git` ou la racine du workspace) :

1. **Dossiers de personnalisation inspectés :**
   - `.agents/`
   - `.agent/`
   - `_agents/`
   - `_agent/`
2. **Configuration Globale :**
   - `~/.gemini/config/` (ou `$HOME/.gemini/config/`)
3. **Composants natifs (Built-ins) :**
   - Chargés directement par nom depuis le bundle applicatif AGY.

---

## 2. Échelle de Précédence Officielle (Niveaux 1 à 5)

En cas de collision de noms (deux skills ou plugins portant le même identifiant), le conflit est résolu strictement selon l'ordre décroissant suivant :

| Niveau | Source de Configuration | Scope | Écrase |
| :---: | :--- | :--- | :--- |
| **1** | **Workspace Project** (`.agents/` hiérarchique) | Projet local | Niveaux 2, 3, 4, 5 |
| **2** | **Declared Configurations** (`skills.json`, `plugins.json` locaux) | Projet déclaré | Niveaux 3, 4, 5 |
| **3** | **Global Discovery** (`~/.gemini/config/`) | Machine locale | Niveaux 4, 5 |
| **4** | **Built-in Customizations** (Fournis par le binaire AGY) | Système | Niveau 5 |
| **5** | **Global Declared Configurations** (`~/.gemini/config/*.json`) | Machine déclarée | Aucun |

---

## 3. Algorithme de Déduplication & Budget de Contexte

- **Déduplication par chemin absolu résolu :** Même si une règle ou un skill est référencé par plusieurs nœuds de l'arbre, son inclusion dans le prompt système est strictement idempotente.
- **Progressive Disclosure :** Les skills n'injectent que leur en-tête YAML (`name` et `description`). Le corps du texte n'est injecté que sur demande expresse.

---

## 4. Outil d'Audit Exécutable

Le script `audit_discovery.py` permet d'inspecter et simuler la résolution du noyau pour n'importe quel dossier :

```powershell
python ./scripts/audit_discovery.py --target-dir "C:\mon\projet" --verbose
```

### Critères de Succès de l'Audit :
- Détection exacte de la racine de dépôt.
- Résolution ordonnée de tous les dossiers `.agents/`.
- Détermination sans ambiguïté du niveau de précédence effectif (1 à 5).
