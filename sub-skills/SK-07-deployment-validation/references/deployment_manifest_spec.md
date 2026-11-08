# Spécification des Manifestes de Déploiement (SK-07)

Ce document décrit le fonctionnement des fichiers de manifestes déclaratifs `skills.json` et `plugins.json`.

---

## 1. Schéma des Entrées (`entries`)

Chaque élément du tableau `entries` référence un répertoire contenant des personnalisations scannées à **un seul niveau de profondeur** :

- **`path`** (chaîne, obligatoire) : Chemin absolu, relatif à `~` ou relatif à la racine du dépôt.
- **`include_only`** (tableau de motifs, optionnel) : Filtre d'inclusion restreignant le chargement aux sous-dossiers correspondants.
- **`exclude`** (tableau de motifs, optionnel) : Motifs d'exclusion pour ignorer des compétences ou plugins obsolètes ou expérimentaux.

---

## 2. Fusion d'Héritage (`inherits`)

Le tableau `inherits` permet d'importer en cascade des manifestes distants ou partagés par l'organisation. L'évaluation s'effectue dans l'ordre de déclaration : les définitions locales complètent et enrichissent les règles importées.
