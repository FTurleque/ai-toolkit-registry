# Instructions de projet

Les fichiers de **contexte projet** : ce que Claude lit automatiquement au démarrage d'une session
dans un dépôt, sans qu'on le lui demande. C'est l'endroit où vivent les conventions d'une base de
code, ses commandes de build, ses pièges et ses règles non écrites.

Le contenu le plus transversal du registre : un bon gabarit de `CLAUDE.md` se réutilise sur tous
vos dépôts, et c'est souvent lui qui fait la plus grande différence sur la qualité du travail d'un
agent.

## Forme attendue

```text
instructions/<nom-du-jeu>/
├── metadata.yaml   métadonnées du registre (obligatoire)
├── README.md       à quel type de projet ça s'applique, et pourquoi (obligatoire)
├── CLAUDE.md       le gabarit lui-même (facultatif)
├── rules/          des règles, une par fichier (facultatif)
└── examples/       une version remplie pour un projet réel
```

Un jeu d'instructions porte un `CLAUDE.md`, des règles, ou les deux. Il peut porter plusieurs
fichiers quand le projet en a besoin : un `CLAUDE.md` racine et des `CLAUDE.md` par module, par
exemple.

## Règles (`rules/`)

Une **règle** est un fichier Markdown que Claude Code charge depuis `.claude/rules/` : même
mécanisme qu'un `CLAUDE.md` (du contexte lu sans qu'on le demande), découpé en un fichier par
sujet. C'est pourquoi les règles vivent ici et non dans un dossier à part : le dossier dit le
mécanisme ([ARCH-001](../.archgate/adrs/ARCH-001-storage-by-mechanism.md)).

- Sans front matter, une règle est chargée au démarrage, avec la priorité d'un `CLAUDE.md`.
- Avec un front matter `paths:` (liste de motifs glob), elle n'est chargée que lorsque Claude
  travaille sur un fichier correspondant. C'est le seul champ lu.
- Une règle s'installe et se retire seule, sans réécrire un `CLAUDE.md` : le bon format pour une
  consigne transverse.

Une règle installée par une skill (par exemple celle d'`arc42-architecture`) reste dans la skill,
comme ressource : elle fait partie de ce que la skill met en place.

## Où Claude les lit

| Fichier | Portée |
|---------|--------|
| `<projet>/CLAUDE.md` | le dépôt, versionné et partagé avec l'équipe |
| `<projet>/CLAUDE.local.md` | le dépôt, mais local — à ignorer dans git |
| `<projet>/<module>/CLAUDE.md` | chargé quand Claude touche ce module |
| `<projet>/.claude/rules/*.md` | le dépôt, une règle par fichier, éventuellement limitée par `paths:` |
| `~/.claude/CLAUDE.md` | tous vos projets |
| `~/.claude/rules/*.md` | tous vos projets, une règle par fichier ; chargées avant les règles du projet, qui l'emportent |
| `<projet>/AGENTS.md` | convention inter-outils, lue par Claude Code et d'autres agents |

## Ce qui fait un bon fichier d'instructions

- Des faits vérifiables, pas des intentions : la commande exacte pour lancer les tests, pas « les
  tests doivent passer ».
- Ce qu'un nouvel arrivant se ferait dire à l'oral le premier jour : le piège qui fait perdre deux
  heures, la règle qui n'est écrite nulle part.
- Court. Ce fichier est chargé à chaque session : chaque ligne inutile coûte du contexte à toutes
  les conversations du dépôt.
- Pas de duplication avec un README : le README explique le projet à un humain, le `CLAUDE.md`
  dit à un agent comment y travailler.

## Installation

- **Gabarit de projet** : copier le `CLAUDE.md` à la racine du dépôt cible et le remplir, et ses
  règles dans `<projet>/.claude/rules/`. Rien à installer dans `~/.claude`.
- **Règles personnelles** (portée utilisateur, comme `user-global-rules`) : copier les fichiers de
  `rules/` dans `~/.claude/rules/`. Ce sont des consignes génériques, valables pour tout dépôt ; la
  configuration propre à une application reste dans son dépôt
  ([GEN-002](../.archgate/adrs/GEN-002-transversal-artifacts-only.md)).

Vérifier avec `/memory` dans une nouvelle session : les fichiers chargés y sont listés.
