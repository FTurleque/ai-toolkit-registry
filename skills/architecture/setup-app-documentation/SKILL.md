---
kind: skill
name: setup-app-documentation
displayName: Mise en place de la documentation d'une application
description: >-
  Met en place, organise et complète toute la documentation d'une application dans docs/ :
  arborescence par lecteur (user/, developer/, architecture/, project/), aiguillage docs/README.md,
  index par dossier, migration des pages existantes par git mv avec table de correspondance, et
  installe la règle .claude/rules/documentation.md qui garde ce rangement. Délègue docs/architecture/
  au skill arc42-architecture (ADR au format Archgate dans docs/architecture/adr/). Vérifie si
  Archgate est installé pour le pointer sur ce registre, et si un superviseur de code est installé
  pour placer ses rapports dans docs/project/rapport-supervisor/. À utiliser dès qu'il faut
  structurer, ranger, réorganiser, auditer ou initialiser la documentation d'un dépôt, même sans le
  mot « documentation » : « range les docs », « mets de l'ordre dans docs/ », « on a deux dossiers
  d'ADR », « prépare la doc du projet », « où mettre ce fichier », ou un docs/ en vrac. Audite et
  propose un plan d'abord ; n'écrit et ne déplace qu'après validation explicite.
version: 1.0.0
status: experimental
category: architecture
tags:
  - documentation
  - docs
  - arc42
  - adr
  - archgate
  - code-supervisor
compatibility:
  - claude-code
requires:
  - git
  - python>=3.8 (facultatif, pour check_docs.py)
authors:
  - Fabrice Turleque
license: MIT
---

# Skill `setup-app-documentation`

> **But** : donner à une application une documentation rangée par lecteur, complète dans sa
> structure, et une règle qui l'empêche de se désorganiser.

Skill générique : il fonctionne dans n'importe quel dépôt, et ne suppose ni langage, ni outil de
build. Tout est découvert dans le dépôt. Langue de production : celle de la documentation existante,
le français à défaut.

Pourquoi ce soin : une documentation sans place assignée se duplique, deux registres d'ADR
divergent, et l'historique du projet finit par noyer la documentation active. Le rangement par
**lecteur** (qui utilise, qui construit, qui décide, qui pilote) donne à chaque page une seule place
évidente.

## Fichiers embarqués

| Fichier | Quand le lire |
|---|---|
| `resources/layout.md` | toujours : arborescence, table « lecteur → emplacement », dossiers facultatifs, anciens emplacements |
| `resources/tooling.md` | toujours en phase 1 (détection), puis en phase 2 pour configurer Archgate et le superviseur |
| `resources/templates/indexes.md` | phase 2, pour écrire `docs/README.md` et les index de dossier |
| `resources/templates/rule-documentation.md` | phase 2, règle à installer dans `<application>/.claude/rules/` |
| `resources/check_docs.py` | phase 1 (état initial) et phase 3 (vérification) |

Lancer le script depuis la racine de l'application, avec son chemin complet :
`python <dossier du skill>/resources/check_docs.py --root .` (`--json` pour une sortie exploitable,
`--self-test` pour vérifier le script). Le dossier du skill est `${CLAUDE_SKILL_DIR}` s'il est défini,
sinon `~/.claude/skills/setup-app-documentation/`.

## Le skill voisin : `arc42-architecture`

`docs/architecture/` est produit par le skill `arc42-architecture` (sections arc42, C4, ADR, règle
`arc42-architecture.md`). Ce skill-ci crée l'arborescence d'ensemble et laisse ce dossier à son
voisin : il ne rédige pas de section arc42 ni d'ADR lui-même. Sa partie à lui dans l'architecture
se limite à vérifier que le registre d'ADR est unique et bien placé.

- Installé (`${CLAUDE_SKILL_DIR}/../arc42-architecture/` ou `~/.claude/skills/arc42-architecture/`) :
  lire son `SKILL.md` et suivre ses phases pour `docs/architecture/`, dans le même plan. Sa règle
  `.claude/rules/arc42-architecture.md` est installée dès que `docs/architecture/` est touché, même
  si seules certaines sections sont écrites : la règle de documentation y renvoie.
- Absent : créer seulement `docs/architecture/README.md` (lien vers le futur dossier arc42) et
  `docs/architecture/adr/`, et le signaler.

Quand les sections arc42 ne sont pas toutes écrites, `docs/architecture/README.md` ne lie que ce qui
existe et liste le reste sans lien, sous « À écrire » : le gabarit d'`arc42-architecture` suppose
les 12 sections présentes, et `check_docs.py` signale chaque lien vers un fichier absent.

---

## Règle absolue — auditer avant d'écrire

**Phase 1 — Audit** : inventaire, détection des outils, plan → **ARRÊT**.
**Phase 2 — Mise en place** : uniquement après validation explicite (« OK », « Go », « Validé »,
ou toute approbation claire). Une description, un contexte ou le silence ne valent pas validation.
**Phase 3 — Vérification**, puis rapport de fin.

Si l'utilisateur ne demande qu'un audit (« audite la doc », « dis-moi ce qui ne va pas »), s'arrêter
au rapport de phase 1.

Une demande ponctuelle (« où ranger ce fichier ? ») dans un dépôt déjà organisé n'est pas une mise en
place : répondre avec la table « lecteur → emplacement » et la règle installée, sans dérouler les phases.

---

## Phase 1 — Audit

1. **Contexte** : racine Git, branche, état (`git status --short`) ; `README.md`, `CLAUDE.md`,
   `.claude/rules/*.md` (une règle de documentation existe-t-elle déjà ?) ; langage et outils de
   build ; CI.
2. **Inventaire de la documentation** : tous les `.md`, `.adoc`, `.rst` hors code généré et
   dépendances (`node_modules/`, `target/`, `build/`, `vendor/`). Pour chaque fichier : lecteur visé,
   emplacement cible (`resources/layout.md`), relevé daté ou page vivante.
3. **Chemins épinglés** : pour chaque fichier à déplacer, chercher qui le cite (code, tests,
   scripts, workflows, hooks, `.claude/`), sous ses deux écritures (`docs/x` et `docs\x`). Un fichier
   cité par un outil se déplace avec la mise à jour de la citation, ou ne se déplace pas.
4. **Outils** (`resources/tooling.md`) : Archgate (CLI, `.archgate/`, `paths.adrs`, nombre d'ADR et
   de règles) ; superviseur de code (plugin, hook global ou projet, `supervisor.config.json`) ;
   skill `arc42-architecture`.
5. **État initial** : `check_docs.py --root .` s'il y a déjà un `docs/`.
6. **Rapport**, au format ci-dessous, puis arrêt.

### Rapport d'audit

```markdown
## Documentation — audit de {application}

### Outils
- Archgate : {installé (version) | absent} · projet configuré : {oui | non} · registre : {chemin}
- Superviseur : {code-supervisor (plugin | manuel) | autre : … | absent} · log_subdir : {valeur | —}
- Skill arc42-architecture : {installé | absent}

### Constat
{5 lignes au plus : ce qui existe, ce qui est en double, ce qui est mal rangé, ce qui manque.}

### Plan de rangement
| # | Fichier actuel | Destination | Lecteur | Cité par | Action |
|---|---|---|---|---|---|
| 1 | docs/adr/0003-postgres.md | docs/architecture/adr/DATA-001-postgresql-storage.md | décision | — | git mv + conversion Archgate |

### Pages à créer
{index, aiguillage, pages manquantes évidentes ; une page à contenu n'est créée que si le dépôt
fournit de quoi l'écrire, sinon elle va dans « À écrire » de son index}

### Configuration
- `.claude/rules/documentation.md` : {créer | fusionner avec l'existant}
- Archgate : {paths.adrs, lint/, .gitignore | rien : absent}
- Superviseur : {.claude/supervisor.config.json | rien : absent}
- arc42 : {phases du skill arc42-architecture | squelette seul : skill absent}

### Questions ouvertes
{décisions qui reviennent à l'utilisateur : page mixte à couper, dossier facultatif à garder…}
```

Conclure par : **Prêt à mettre en place la documentation. Confirmez pour continuer (phase 2).**

---

## Phase 2 — Mise en place

Dans cet ordre :

1. **Arborescence** : les quatre dossiers de premier niveau, et seulement les dossiers facultatifs
   qui recevront un contenu (`resources/layout.md`). Ne jamais écraser un fichier existant sans dire
   précisément ce qui est remplacé.
2. **Déplacements** : `git mv`, jamais suppression puis recréation. Puis, pour chaque déplacement :
   mettre à jour les citations trouvées en phase 1, recalculer les liens relatifs des pages déplacées
   et de celles qui pointent vers elles, ajouter la ligne à la table de correspondance de
   `docs/project/README.md`. La **prose** d'un relevé daté ne se réécrit pas, seuls ses liens. Un
   relevé daté déplacé prend le nom de la convention (`AUDIT_<objet>_<AAAA-MM-JJ>.md`) si sa date est
   établie par son contenu ; sinon il garde son nom. Le renommage figure dans la table.
3. **Pages mixtes** : les couper en une page `user/` et une page `developer/` qui se citent, si
   l'utilisateur l'a validé.
4. **Architecture** : dérouler le skill `arc42-architecture` pour `docs/architecture/` (ou le
   squelette minimal s'il est absent). Les ADR sont au format Archgate, dans `docs/architecture/adr/`,
   qui ne contient rien d'autre. Une ADR d'un autre format se **convertit** sans être réécrite
   (`resources/tooling.md`, « Convertir une ADR d'un autre format »).
5. **Index** : `docs/README.md` (aiguillage seul), puis un `README.md` par dossier qui contient des
   pages (`resources/templates/indexes.md`). Une page citée existe ; une page à écrire est listée
   sans lien.
6. **Archgate**, s'il est installé : configuration de `resources/tooling.md` (`paths.adrs`, `lint/`,
   `.gitignore`, déplacement des ADR de `.archgate/adrs/`, contrôle du nombre d'ADR et de règles).
   Absent : rien sous `.archgate/`.
7. **Superviseur**, s'il est installé : `.claude/supervisor.config.json` (`log_subdir`,
   `quiet_paths`), fusionné avec l'existant. Absent : rien.
8. **Règle** `<application>/.claude/rules/documentation.md` depuis
   `resources/templates/rule-documentation.md` : garder les blocs des outils configurés, retirer les
   autres et les dossiers facultatifs non créés. Fichier déjà présent : comparer, proposer une
   fusion, ne pas écraser.
9. **Référencer** : une ligne dans le `CLAUDE.md` de l'application (ou `.claude/CLAUDE.md`) qui
   renvoie à `docs/README.md` et à la règle, et un lien vers `docs/README.md` depuis le `README.md`
   racine. Sans `CLAUDE.md`, sa création figure au plan de la phase 1 (un fichier court : ces deux
   renvois) et ne se fait que validée.

Ne rien commiter sauf demande explicite.

---

## Phase 3 — Vérification

- `check_docs.py --root .` : **zéro erreur**. Chaque avertissement restant est soit corrigé, soit
  justifié dans le rapport.
- Plus aucune occurrence d'un ancien chemin déplacé dans le dépôt : `git grep --untracked` sur
  chaque ancien chemin, sous ses deux écritures. Restent admis : les relevés datés, la table de
  correspondance, la liste des anciens emplacements interdits de la règle, et la ligne « Ancien
  emplacement » des `References` d'une ADR convertie.
- Archgate configuré : `archgate adr list` liste les identifiants d'avant la migration **plus** ceux
  des ADR converties, exactement ceux du plan ; `archgate check --output json` n'a pas
  d'`unparsedAdrs`, et le `total` des règles n'a pas baissé. `total: 0` ne prouve rien : il signifie
  qu'aucune règle n'a été exécutée. `check` génère `docs/architecture/rules.d.ts`, ignoré par Git :
  c'est attendu.
- Superviseur configuré : `.claude/supervisor.config.json` est un JSON valide ; ne pas créer le
  dossier de rapports à la main.
- Les tests et validateurs du dépôt qui lisent des chemins de documentation passent, s'ils existent.

### Rapport de fin

```markdown
## Documentation — {application}

### Fichiers
✅ créés : {n} · 🔀 déplacés : {n} (table dans docs/project/README.md) · ✏️ modifiés : {n}
✅ .claude/rules/documentation.md
✅ .archgate/config.json — paths.adrs (ou : Archgate absent, rien écrit)
✅ .claude/supervisor.config.json — log_subdir (ou : superviseur absent, rien écrit)

### Contrôles
{commande · résultat} pour check_docs.py, git grep, archgate, tests du dépôt

### Reste à faire
{pages « À écrire », questions ouvertes, avertissements justifiés, installations proposées}
```

---

## Règles de vérité

- Ne pas inventer de contenu : une page n'est écrite que si le dépôt, une page existante ou
  l'utilisateur fournit de quoi l'écrire. Sinon elle est annoncée, pas fabriquée.
- Un outil n'est « installé » que si la détection l'a montré. Ne jamais installer Archgate ni le
  superviseur soi-même, ne jamais lancer `archgate init` sans demande explicite.
- Ce qui n'est pas confirmé porte `Hypothèse à valider` dans le rapport.
