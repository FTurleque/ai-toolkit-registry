# Fichiers et dossiers créés

Ne crée jamais de dossier, de worktree ni de fichier hors du dépôt sur lequel tu travailles : ni à
côté de lui (par exemple `../<nom>`), ni ailleurs sur le poste.

- **Worktrees** : `git worktree add .claude/worktrees/<nom> ...`, jamais `../<nom>`. Si
  `/.claude/worktrees/` n'est pas dans le `.gitignore` du dépôt, signale-le et propose de l'ajouter
  avant de créer le worktree.
- **Artefacts à conserver** (installeurs, archives de release, sorties de build téléchargées) :
  dans le dossier de build ignoré du dépôt (`target/`, `build/`, `dist/`…). Vérifie qu'il est bien
  ignoré par Git avant d'y écrire. S'il n'en existe aucun, demande où ranger les fichiers.
- **Fichiers temporaires** (scripts, sorties intermédiaires, extractions) : le scratchpad de la
  session.
- Si une tâche impose malgré tout d'écrire hors du dépôt, demande d'abord, puis supprime ce que tu
  as créé en fin de tâche.
