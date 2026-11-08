---
name: sk-03-skill-authoring
description: >-
  Sous-skill SK-03 : Ingénierie et scaffolding de compétences modulaires Antigravity.
  À activer pour structurer un skill conforme (frontmatter YAML, dossier skills/<name>/),
  appliquer le principe de divulgation progressive et automatiser les procédures d'outillage.
---

# SK-03 — Modular Skill Authoring

Ce sous-skill définit la méthodologie standard pour concevoir, rédiger et structurer des compétences d'agent (Skills) hautement performantes et économes en contexte.

---

## 1. Structure Canonique d'un Skill

Un skill Antigravity doit obligatoirement résider dans un sous-répertoire sous un dossier `skills/` :

```text
skills/<skill_name>/
├── SKILL.md          # Obligatoire : Frontmatter YAML + Procédures pas-à-pas
├── scripts/          # Optionnel : Scripts d'aide exécutables (Python, Bash, PS1)
├── examples/         # Optionnel : Exemples de code et cas d'usage réels
├── resources/        # Optionnel : Gabarits, assets et fichiers modèles
└── references/       # Optionnel : Spécifications lourdes et manuels détaillés
```

---

## 2. Spécification du Frontmatter `SKILL.md`

Le fichier d'instruction principal débute impérativement par un bloc YAML valide :

```yaml
---
name: mon-skill-specialise
description: >-
  Description explicite à la 3e personne. Doit préciser avec exactitude CE QUE
  fait le skill et QUAND l'agent doit l'activer.
---
```

### Directives de Qualité du `description` :
- **Clé de déclenchement :** C'est l'unique champ analysé par l'agent lors de la sélection initiale.
- **Formulation impérative :** Doit inclure des mots-clés distinctifs et des déclencheurs situationnels.
- **Longueur optimale :** 2 à 4 phrases claires.

---

## 3. Divulgation Progressive (Progressive Disclosure)

Pour minimiser la consommation de la fenêtre de contexte :
1. Le corps de `SKILL.md` ne contient que le résumé exécutable et les étapes opérationnelles directes.
2. Toute documentation dépassant 50 lignes est déportée dans `references/<sujet>.md`.
3. Les chaînes de commandes complexes sont isolées dans des scripts exécutables dans `scripts/`.

---

## 4. Outil de Scaffolding et de Validation

Le script `scaffold_skill.py` permet d'échafauder un nouveau skill complet ou de valider la conformité d'un skill existant :

```powershell
# Création d'un nouveau skill
python ./scripts/scaffold_skill.py --action create --name "db-optimizer" --target-dir "./skills"

# Audit d'un skill existant
python ./scripts/scaffold_skill.py --action validate --path "./skills/db-optimizer"
```
