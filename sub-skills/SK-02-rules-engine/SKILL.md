---
name: sk-02-rules-engine
description: >-
  Sous-skill SK-02 : Conception, gouvernance et validation des règles d'espace de travail
  Antigravity (GEMINI.md, AGENTS.md). À activer pour auditer la conformité au plafond de 24 Ko,
  le respect du budget global de 20 000 tokens, la gestion des inclusions @[label](path)
  et la portée hiérarchique par répertoire.
---

# SK-02 — Rules Engine & Governance

Ce sous-skill régit la création, l'héritage et la validation des règles de comportement de l'agent. Les règles permettent d'imposer des contraintes de sécurité, des standards de code et des restrictions d'API locales ou globales.

---

## 1. Types et Emplacements des Règles

1. **Règles par Répertoire (`GEMINI.md` / `AGENTS.md`) :**
   - Placés directement dans n'importe quel dossier.
   - S'appliquent au répertoire hôte et à **tous ses sous-répertoires**.
   - Pas de frontmatter YAML : le contenu markdown pur est inconditionnellement injecté (`always_on`).
2. **Règles Modulaires (`.agents/rules/*.md`) :**
   - Stockées dans les répertoires de règles dédiés.
   - Supportent le déclenchement conditionnel ou contextuel.
3. **Règles Embarquées dans les Plugins (`plugins/<nom>/rules/AGENTS.md`) :**
   - Chargées automatiquement lorsque le plugin hôte est actif.

---

## 2. Plafonds d'Octets et Budget de Tokens

Le moteur Antigravity applique des garde-fous stricts pour préserver la fenêtre de contexte du modèle :

- **Plafond Individuel par Fichier :** **24 000 octets (24 Ko)**.
  - Tout fichier dépassant 24 000 octets (après résolution des inclusions `@[label](path)`) subit une **troncature déterministe** alignée sur la dernière limite de ligne valide.
- **Budget Partagé Global :** **20 000 tokens (`defaultRulesBudget`)**.
  - Si la somme des règles actives excède ce quota, le moteur opère une **rétrogradation automatique (demotion)** : les règles les plus basses dans la priorité sont converties en pointeurs de chemin de fichier au lieu d'être injectées en ligne dans le prompt système.
- **Exception Native :** Les règles fournies par les plugins built-in sont exemptées de cette limite de budget.

---

## 3. Mécanisme d'Inclusion `@[label](path)`

Il est possible de modulariser une règle volumineuse via la syntaxe d'inclusion :
```markdown
# Section Principale
@[Guidelines de Sécurité](./security_guidelines.md)
```
Le moteur résout le chemin relatif et insère le contenu de la cible avant le calcul du quota des 24 Ko.

---

## 4. Outil de Validation Exécutable

Le script `validate_rules.py` audite la conformité d'un fichier ou d'une arborescence de règles :

```powershell
python ./scripts/validate_rules.py --path "C:\mon\projet" --max-bytes 24000 --budget-tokens 20000
```

### Vérifications Automatisées :
- [x] Absence d'en-tête YAML illégal dans `AGENTS.md` / `GEMINI.md`.
- [x] Respect strict du plafond de 24 000 octets.
- [x] Résolution et validation des cibles `@[label](path)`.
- [x] Estimation du coût en tokens (méthode $1 \text{ token} \approx 4 \text{ caractères}$).
