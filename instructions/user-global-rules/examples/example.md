# Exemple — un worktree demandé en cours de session

**Demande** (en anglais) : « Create a worktree to try the refactoring on a separate branch. »

**Avec les deux règles installées**

- Claude répond en français (`language.md`), le nom de branche et le message de commit restant en
  anglais si c'est la convention du dépôt.
- Il vérifie que `/.claude/worktrees/` est ignoré par Git ; ce n'est pas le cas, il le signale et
  propose de l'ajouter au `.gitignore` (`files-outside-repo.md`).
- Après accord : `git worktree add .claude/worktrees/refactoring-invoices -b refactoring-invoices`.

**Sans les règles** : réponse en anglais, et `git worktree add ../refactoring-invoices`, qui crée
un dossier à côté du dépôt.
