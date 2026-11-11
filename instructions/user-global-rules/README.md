# Règles personnelles transverses

Deux règles à installer **une fois** dans `~/.claude/rules/`, pour qu'elles s'appliquent à toutes
vos sessions, dans tous vos dépôts, sans toucher au `CLAUDE.md` de chaque projet.

| Fichier | Ce qu'il impose |
|---------|-----------------|
| `rules/language.md` | répondre en français, quelle que soit la langue de la demande ou des fichiers ; code, identifiants et commits suivent le projet |
| `rules/files-outside-repo.md` | ne rien créer hors du dépôt de travail : worktrees dans `.claude/worktrees/`, artefacts dans le dossier de build ignoré, temporaires dans le scratchpad ; demander avant toute exception |

## Ce que ça change

- **Langue** : plus besoin de le redemander à chaque session, ni de le répéter dans chaque dépôt.
- **Hors du dépôt** : fin des worktrees `../<nom>` et des fichiers semés à côté des dépôts ou dans
  le dossier personnel, qu'on découvre des semaines plus tard.

## Pourquoi des règles et pas un `CLAUDE.md`

Une règle de `~/.claude/rules/` est chargée au démarrage avec la même priorité qu'un `CLAUDE.md`
utilisateur, mais elle vit dans son propre fichier : on installe, met à jour ou retire une règle
sans réécrire un fichier qui contient aussi d'autres consignes. C'est le format adapté à un
registre. Une règle de projet (`<projet>/.claude/rules/`) est chargée après les règles utilisateur
et l'emporte en cas de conflit.

## Installation

```bash
mkdir -p ~/.claude/rules
cp instructions/user-global-rules/rules/*.md ~/.claude/rules/
```

Ne copier que les règles voulues : chaque fichier est indépendant. Pour changer de langue,
modifier `language.md` après copie. Si les mêmes consignes figurent déjà dans
`~/.claude/CLAUDE.md`, les en retirer pour ne pas les avoir en double.

Vérifier : dans une nouvelle session, `/memory` liste les fichiers de `~/.claude/rules/` chargés.

## Limites

- Ce sont des consignes, pas des contrôles : rien n'empêche techniquement une écriture hors du
  dépôt. Pour une garantie, il faudrait un hook `PreToolUse`.
- `files-outside-repo.md` suppose que le dépôt ignore `/.claude/worktrees/` ; la règle demande de
  le signaler quand ce n'est pas le cas.
- Pas de champ `paths:` : ces règles s'appliquent partout, ce qui est leur raison d'être.
- Vérifié dans Claude Code, où ces consignes étaient appliquées depuis `~/.claude/CLAUDE.md` ; le
  chargement depuis `~/.claude/rules/` se vérifie avec `/memory`.
