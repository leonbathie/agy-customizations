# Checklists de Validation Multi-Niveaux (AGY-CUSTOMIZATIONS)

Ce document répertorie l'ensemble des critères d'acceptation et points de contrôle pour chacun des niveaux du système de personnalisation Antigravity.

---

## Niveau 0 : Diagnostic Initial & Résolution du Noyau (agent-kernel / SK-01)
- [x] **CHK-001** : Détection sans ambiguïté de la racine du dépôt git (présence de `.git`).
- [x] **CHK-002** : Traversée ascendante exhaustive depuis le CWD jusqu'à la racine du dépôt.
- [x] **CHK-003** : Détection des dossiers pivots autorisés (`.agents/`, `.agent/`, `_agents/`, `_agent/`).
- [x] **CHK-004** : Application déterministe des 5 niveaux de précédence sans conflit d'écrasement erroné.
- [x] **CHK-005** : Déduplication stricte par chemin canonique absolu résolu (`realpath`).

---

## Niveau 1 : Gouvernance des Règles d'Espace de Travail (agent-rules / SK-02)
- [x] **CHK-101** : Respect absolu du plafond de **24 000 octets** par fichier de règles.
- [x] **CHK-102** : Résolution récursive sans boucle infinie des inclusions `@[label](path)`.
- [x] **CHK-103** : Absence totale de frontmatter YAML dans les fichiers `AGENTS.md` / `GEMINI.md` autonomes.
- [x] **CHK-104** : Respect du budget cumulé partagé de **20 000 tokens** (`defaultRulesBudget`).
- [x] **CHK-105** : Vérification de la portée récursive descendante (application aux sous-répertoires).

---

## Niveau 2 : Ingénierie des Compétences Modulaires (agent-skill / SK-03)
- [x] **CHK-201** : Présence obligatoire du fichier `SKILL.md` sous `skills/<nom-du-skill>/`.
- [x] **CHK-202** : Frontmatter YAML valide avec délimiteurs `---` stricts.
- [x] **CHK-203** : Champ `name` conforme à la casse slug minuscules avec tirets (`^[a-z0-9]+(-[a-z0-9]+)*$`).
- [x] **CHK-204** : Champ `description` explicite, formulé à la 3e personne avec déclencheurs clairs.
- [x] **CHK-205** : Respect de la divulgation progressive (corps de `SKILL.md` concis, renvoi vers `references/` et `scripts/`).

---

## Niveau 3 : Empaquetage et Manifestes de Plugins (agent-plugin / SK-04)
- [x] **CHK-301** : Présence obligatoire du manifeste racine `plugin.json`.
- [x] **CHK-302** : Règle stricte d'ingestion native : `hooks.json` placé à la racine du plugin (`<plugin_dir>/hooks.json`).
- [x] **CHK-303** : Isolation des outils et compétences embarqués par espace de noms (namespacing).
- [x] **CHK-304** : Gestion d'état dans `~/.gemini/config/config.json` avec victoire de la préférence utilisateur sur le défaut.
- [x] **CHK-305** : Consolidation réussie des sous-dossiers optionnels (`skills/`, `rules/`, `mcp_config.json`).

---

## Niveau 4 : Gardes et Intercepteurs de Cycle de Vie (agent-hook / SK-05)
- [x] **CHK-401** : Validation structurelle des événements groupés (`PreToolUse`, `PostToolUse`) avec encapsulation `matcher` + `hooks`.
- [x] **CHK-402** : Validation structurelle des événements plats (`SessionStart`, `PreInvocation`, `PostInvocation`, `Stop`).
- [x] **CHK-403** : Gestion des timeouts par hook pour prévenir tout blocage indéfini.
- [x] **CHK-404** : Comportement de blocage déterministe sur code de sortie non-nul en phase `PreToolUse`.
- [x] **CHK-405** : Fusion ordonnée (merging) des hooks multiples sans perte de configuration.

---

## Niveau 5 : Intégrations et Protocoles MCP (agent-mcp / SK-06)
- [x] **CHK-501** : Clé racine `mcpServers` conforme dans `mcp_config.json`.
- [x] **CHK-502** : Pour le transport Stdio : présence du binaire `command`, arguments `args` en liste, environnement `env` isolé.
- [x] **CHK-503** : Pour le transport HTTP : URL Streamable HTTP conforme à la spécification du 26 mars 2025 (`/mcp`).
- [x] **CHK-504** : Rejet des configurations hybrides illégales mélangeant `command` et `url`.
- [x] **CHK-505** : Zéro secret ou token d'authentification en clair dans les arguments de processus.

---

## Niveau 6 : Déploiement Déclaratif et CI/CD (agent-deployer / SK-07)
- [x] **CHK-601** : Validité syntaxique des manifestes déclaratifs `skills.json` et `plugins.json`.
- [x] **CHK-602** : Résolution correcte des 3 modes de chemins : absolu, relatif home (`~`), relatif workspace (racine git).
- [x] **CHK-603** : Validation des motifs d'inclusion (`include_only`) et d'exclusion (`exclude`).
- [x] **CHK-604** : Analyse d'héritage en cascade (`inherits`) sans boucle de dépendance.
- [x] **CHK-605** : Exécution de la suite de tests en mode strict (`--strict-ci`) avec zéro avertissement toléré.

---

## Niveau 7 : Intégration Maître de Bout en Bout
- [x] **CHK-701** : Les 7 sous-skills sont fonctionnels et validés par tests unitaires.
- [x] **CHK-702** : Les 7 sous-agents sont correctement déclarés avec manifestes et system prompts.
- [x] **CHK-703** : L'orchestrateur global (`orchestrator.py`) confirme l'état de santé `HEALTHY`.
- [x] **CHK-704** : Le runner de matrice (`run_matrix_checks.py`) atteint 100% de succès.
