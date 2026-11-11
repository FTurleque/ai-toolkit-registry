# Exemple — rassembler le contexte d'une évolution

**Demande** : « Prépare-moi le contexte pour ajouter un champ `priority` aux tickets. »

**Ce que fait Claude avec NEXUS branché**

1. `list_projects` pour identifier le projet.
2. `build_context` avec la demande : NEXUS rend les fichiers et sections pertinents (modèle,
   persistance, API, documentation, instructions du dépôt) dans le budget demandé.
3. `explain_context` si un élément surprend : pourquoi il a été retenu.
4. Claude travaille sur ce contexte et cite les éléments utilisés.

**Sans NEXUS** : Claude ouvre les fichiers dont le nom évoque les tickets et risque de rater la
migration de base ou la règle du `CLAUDE.md` qui s'applique.
