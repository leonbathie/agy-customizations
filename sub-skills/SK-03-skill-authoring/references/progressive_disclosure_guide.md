# Guide de Divulgation Progressive des Compétences (SK-03)

La divulgation progressive (Progressive Disclosure) est la technique fondamentale permettant à Antigravity d'héberger des dizaines de compétences sans saturer la mémoire de travail (contexte) du modèle.

---

## 1. Cycle de Chargement en 2 Temps

1. **Phase d'Amorçage (Boot Phase) :**
   - Seuls le `name` et le `description` du frontmatter YAML sont injectés dans l'index des outils disponibles.
   - Consommation contextuelle : $< 50$ tokens par compétence.
2. **Phase d'Activation (On-Demand Hydration) :**
   - Dès que le modèle détecte que la description correspond à la demande utilisateur, il invoque la lecture du fichier complet `SKILL.md`.

---

## 2. Anatomie d'une Bonne Description YAML

Une description efficace répond à 3 questions en un seul paragraphe :
1. **QUOI** : Quelle est l'expertise technique couverte ?
2. **QUAND** : Quels sont les mots-clés ou situations déclenchantes ?
3. **DIFFÉRENTIATION** : Que ne fait PAS ce skill (éviter le faux-positif) ?

### Contre-exemple :
```yaml
description: Aide avec le SQL et les bases de données.  # Mauvais: trop vague, capte trop de bruit.
```

### Exemple canonique :
```yaml
description: >-
  Optimisation avancée des requêtes SQL pour BigQuery. À activer lorsque l'utilisateur
  demande de réduire les coûts d'exécution, d'analyser le plan d'exécution (EXPLAIN),
  ou de partitionner/clusteriser de grandes tables. Ne pas utiliser pour PostgreSQL ou MySQL.
```
