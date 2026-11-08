# Spécification Formelle de la Précédence Antigravity (SK-01)

Ce document formalise les règles déterministes d'arbitrage et de découverte appliquées par le moteur Antigravity.

---

## 1. Découverte Ascendante (Bottom-Up Traversal)

Lorsqu'une session est initialisée dans le répertoire $D_0$, le système résout la séquence ordonnée de répertoires :
$$S = (D_0, D_1, \dots, D_k)$$
où $D_k$ est la racine du dépôt git (ou la racine du système de fichiers).

Pour chaque répertoire $D_i$, Antigravity recherche l'existence de l'un des répertoires de personnalisation suivants, par ordre de priorité :
1. `$D_i/.agents/`
2. `$D_i/.agent/`
3. `$D_i/_agents/`
4. `$D_i/_agent/`

---

## 2. Matrice d'Arbitrage des Conflits de Noms

Si deux entités partagent le même identifiant $ID$ (par exemple `skill-linter` ou le plugin `developer-pack`) :

| Source A | Source B | Gagnant | Règle d'arbitrage |
| :--- | :--- | :--- | :--- |
| Workspace (`.agents/`) | Declared (`skills.json`) | **Workspace** | Précédence Niveau 1 > Niveau 2 |
| Declared (`skills.json`) | Global (`~/.gemini/config/`) | **Declared** | Précédence Niveau 2 > Niveau 3 |
| Global (`~/.gemini/config/`) | Built-in AGY | **Global** | Précédence Niveau 3 > Niveau 4 |
| Built-in AGY | Global Declared | **Built-in** | Précédence Niveau 4 > Niveau 5 |
| Child Folder ($D_0$) | Parent Folder ($D_1$) | **Child Folder ($D_0$)** | La règle la plus proche du CWD prévaut |

---

## 3. Déduplication et Normalisation des Chemins

1. Chaque ressource découverte est normalisée via son chemin canonique absolu :
   $$\text{canonical\_path} = \text{realpath}(P)$$
2. Le noyau maintient un registre d'unicité `Set<CanonicalPath>`.
3. Une ressource déjà enregistrée est ignorée lors des découvertes ultérieures de la même session, préservant la première occurrence (celle de plus haute précédence).
