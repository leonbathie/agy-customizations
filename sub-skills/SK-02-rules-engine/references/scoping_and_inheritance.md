# Portée et Héritage des Règles Antigravity (SK-02)

Ce document décrit la dynamique d'héritage et les règles de confinement des contraintes de l'agent.

---

## 1. Portée Contextuelle par Répertoire

Toute règle définie dans un fichier `AGENTS.md` ou `GEMINI.md` à la racine d'un dossier $D$ s'applique récursivement :
$$\text{Scope}(D) = D \cup \{ d \in \text{Descendants}(D) \}$$

### Exemple d'héritage :
```text
my-project/
├── AGENTS.md                  # Règle globale du projet (R1)
├── frontend/
│   ├── AGENTS.md              # Règle spécifique frontend (R2)
│   └── src/
│       └── App.tsx            # L'agent opérant ici applique [R1 + R2]
└── backend/
    └── server.py              # L'agent opérant ici applique [R1 uniquement]
```

---

## 2. Rétrogradation Contextuelle (Demotion Protocol)

Lorsque le volume total des règles dépasse le budget de **20 000 tokens** :

1. Les règles les plus profondes dans l'arborescence (les plus proches du fichier édité) sont **préservées en priorité**.
2. Les règles globales excédentaires sont transformées en références :
   ```markdown
   > [RULE REFERENCE]: Path to 'C:\path\to\AGENTS.md' (Consultable à la demande)
   ```
3. L'agent ne charge le texte complet qu'en cas de nécessité avérée.

---

## 3. Directives de Rédaction Efficace

- Éviter la redondance avec la documentation standard des langages.
- Privilégier les listes à puces avec impératifs clairs (`DO`, `DON'T`).
- Limiter les exemples de code inline à moins de 20 lignes.
