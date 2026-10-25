# Gabarit — règle `.claude/rules/documentation.md`

À copier dans `<application>/.claude/rules/documentation.md` en remplaçant `{application}` et
`{date}`. Les blocs `<!-- si Archgate -->` et `<!-- si superviseur -->` ne sont gardés que si l'outil
est installé et configuré ; les retirer sinon, balises comprises. Les autres lignes restent,
dossiers facultatifs compris : la règle dit où ranger un **futur** fichier, même si son dossier
n'existe pas encore. Ne rien ajouter que le dépôt ne vérifie ou n'applique.

Tout ce qui suit la ligne `---8<---` est le contenu du fichier.

---8<---

# Règles — Organisation de `docs/`

> **But** : ranger chaque page de documentation de {application} à sa place du premier coup, et
> garder un seul emplacement par type de document.

L'arborescence de `docs/` est **figée** depuis le {date}. Une page mal rangée se duplique, un
registre parallèle diverge, et une documentation qui ment coûte plus cher qu'une documentation
absente.

## L'arborescence

```text
docs/
  README.md          aiguillage, rien d'autre
  user/              utiliser {application}
    release-notes/   RELEASE_NOTES_<version>.md
  developer/         construire, modifier, étendre {application}
    reference/       contrats machine
  architecture/      dossier arc42 (règle arc42-architecture.md)
    adr/             registre unique des ADR, format Archgate
  project/           piloter et auditer le projet
    governance/      feuille de route, état de la documentation
    roadmap/         <jalon>_EXECUTION.md
    validation/      VALIDATION_<jalon>.md
    audits/          un relevé par date
    product/         cadrage produit
    research/        études et expériences
<!-- si superviseur -->
    rapport-supervisor/  dossier local du superviseur de code, non versionné
<!-- fin si superviseur -->
```

`docs/README.md` est le **seul** fichier à la racine de `docs/`, et `user/`, `developer/`,
`architecture/`, `project/` les **seuls** dossiers de premier niveau. Un nouveau dossier de premier
niveau est une décision de structure : la demander, ne pas la prendre en passant.

## Où ranger un nouveau fichier

Se poser la question du **lecteur**, pas du sujet :

| Le lecteur veut… | Emplacement |
|---|---|
| installer, configurer, lancer une commande, migrer de version | `docs/user/` |
| savoir ce qui change dans une version | `docs/user/release-notes/` |
| compiler, tester, qualifier, comprendre un module | `docs/developer/` |
| lire un contrat machine (OpenAPI, port, modèle, surfaces publiques) | `docs/developer/reference/` |
| comprendre l'architecture d'ensemble, un scénario qualité, un risque | `docs/architecture/` |
| retrouver ou écrire une décision structurante | `docs/architecture/adr/` |
| connaître l'état, les priorités, l'autorité d'un document | `docs/project/governance/` |
| lire le plan d'un jalon | `docs/project/roadmap/` |
| lire la preuve d'un jalon ou d'une release | `docs/project/validation/` |
| lire un audit daté | `docs/project/audits/` |

Un même sujet a souvent **deux pages** : `user/` dit comment s'en servir, `developer/` comment c'est
construit. Écrire deux pages plutôt qu'une page mixte.

## TOUJOURS

- Ranger une page dans **un seul** emplacement ; ne jamais la dupliquer dans un second.
- Ajouter la page à l'index de son dossier (`README.md`) dans le même changement, et à
  `docs/README.md` si elle répond à un besoin de premier niveau.
- Écrire des liens **relatifs** entre pages de `docs/` ; citer un chemin depuis la racine du dépôt
  (`docs/developer/BUILD.md`) partout ailleurs : code, tests, scripts, workflows, `.claude/`.
- Garder une page de `docs/user/` **lisible sans le dépôt** : elle parle du produit installé, de ses
  commandes et de ses fichiers de configuration.
- Ajouter un audit sous `docs/project/audits/` : `AUDIT_<objet>_<AAAA-MM-JJ>.md`, ou un dossier
  `<AAAA-MM-JJ>/` s'il porte plusieurs fichiers ; l'indexer dans `audits/README.md`.
- Écrire une ADR selon la règle `arc42-architecture.md` : `docs/architecture/adr/<PRÉFIXE>-<NNN>-<slug>.md`,
  numéro qui suit le plus haut attribué pour ce préfixe, ligne ajoutée à
  `docs/architecture/arc42/09-decisions.md`.

## JAMAIS

- Jamais de fichier à la racine de `docs/` autre que `README.md`.
- Jamais de nouveau dossier de premier niveau sous `docs/`, ni de retour d'un ancien emplacement
  (`docs/adr/`, `docs/arc42/`, `docs/openapi/`, `docs/reference/`, `docs/release/`,
  `docs/governance/`, `docs/roadmap/`, `docs/validation/`, `docs/audit/`, `docs/audits/`,
  `docs/research/`, `docs/product/`).
- Jamais de second registre d'ADR ni de second dossier d'audits.
- Jamais d'autre fichier qu'une ADR (et son `.rules.ts`) dans `docs/architecture/adr/` : ni index,
  ni gabarit. L'index est la section 9 d'arc42.
<!-- si Archgate -->
- Jamais d'ADR dans `.archgate/adrs/` : Archgate lit `docs/architecture/adr/`
  (`paths.adrs` dans `.archgate/config.json`). `.archgate/` porte la configuration d'Archgate, pas
  de documentation.
<!-- fin si Archgate -->
<!-- si superviseur -->
- Jamais de document versionné sous `docs/project/rapport-supervisor/` : c'est le dossier local du
  superviseur de code (rapports et état de session, ignoré par Git), fixé par `log_subdir` dans
  `.claude/supervisor.config.json`. Jamais de rapport ailleurs : ni `docs/rapport-supervisor/`, ni un
  `docs/` imbriqué dans un sous-dossier.
<!-- fin si superviseur -->
- Jamais dans `docs/user/` : un SHA, un compteur de tests ou de couverture, un numéro d'issue ou de
  PR, une commande de build, un chemin `src/`. C'est du contenu `developer/` ou `project/`.
- Jamais de contenu de pilotage (état d'un jalon, priorités, preuve) dans `docs/developer/`.

## Déplacer ou renommer un fichier de `docs/`

Un chemin de documentation est **épinglé** : du code, des tests, des scripts, des workflows et des
hooks peuvent le citer.

1. Déplacer avec `git mv`, jamais par suppression puis recréation.
2. Chercher l'ancien chemin dans **tout** le dépôt, sous ses deux écritures (`docs/x/` et
   `docs\x\`), et dans les motifs d'expression régulière (`docs[\\/]x[\\/]`).
3. Recalculer les liens relatifs des pages déplacées **et** de celles qui pointent vers elles. Un
   lien redirigé vers un autre document change aussi de libellé. Un fichier compagnon
   (`<ID>-<slug>.rules.ts` d'une ADR) se renomme avec lui.
4. Compléter la table de correspondance de `docs/project/README.md`.
5. Contrôler les liens et la structure :
   `python ~/.claude/skills/setup-app-documentation/resources/check_docs.py` (si le skill est
   installé), puis les tests du dépôt qui lisent ces fichiers.

## Relevés datés — liens oui, prose non

Les plans d'exécution, les `VALIDATION_*`, les audits, les études, les notes de version, les
changements OpenSpec archivés sont des relevés datés. Lors d'un déplacement, leurs **liens** sont
recalculés, leur **prose** n'est pas réécrite : elle cite les chemins de sa date.

## Hors de `docs/`

`README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md` à la racine, et les fichiers lus par
un outil à un emplacement fixe, restent où ils sont.
