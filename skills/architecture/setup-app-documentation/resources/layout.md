# Arborescence cible de `docs/`

Rangement par **lecteur**, pas par sujet : un même sujet a souvent deux pages, une pour celui qui
utilise le produit, une pour celui qui le construit.

## Contents

- Arborescence
- Où ranger un fichier
- Dossiers facultatifs
- Ce qui reste hors de `docs/`
- Relevés datés
- Anciens emplacements courants

---

## Arborescence

```text
docs/
  README.md            aiguillage, rien d'autre
  user/                utiliser l'application
    release-notes/     RELEASE_NOTES_<version>.md
  developer/           construire, modifier, étendre l'application
    reference/         contrats machine (OpenAPI, contrats de ports, modèle de domaine, surfaces publiques)
  architecture/        dossier arc42 (skill arc42-architecture)
    arc42/             12 sections
    adr/               registre unique des ADR, format Archgate, rien d'autre que des ADR
    diagrams/ quality/ risks/
  project/             piloter et auditer le projet
    governance/        feuille de route, état de la documentation, autorité des documents
    roadmap/           <jalon>_EXECUTION.md
    validation/        VALIDATION_<jalon>.md, qualification de release
    audits/            un relevé par date
    product/           cadrage produit
    research/          études et expériences
    rapport-supervisor/  dossier local du superviseur de code, non versionné (si superviseur)
```

Règles de structure :

- `docs/README.md` est le **seul** fichier à la racine de `docs/`.
- `user/`, `developer/`, `architecture/`, `project/` sont les **seuls** dossiers de premier niveau.
  En ajouter un est une décision de structure : la demander.
- Chaque dossier qui contient des pages a un `README.md` qui les indexe, sauf `architecture/adr/`
  (Archgate lirait l'index comme un ADR : l'index des décisions est `arc42/09-decisions.md`).

## Où ranger un fichier

| Le lecteur veut… | Emplacement |
|---|---|
| installer, configurer, lancer une commande, migrer de version | `docs/user/` |
| savoir ce qui change dans une version | `docs/user/release-notes/` |
| compiler, tester, qualifier, comprendre un module | `docs/developer/` |
| lire un contrat machine (OpenAPI, port, modèle, surfaces publiques) | `docs/developer/reference/` |
| appeler l'API de l'application, guide en prose (le produit **est** une API) | `docs/user/` ; le contrat lui-même reste dans `docs/developer/reference/` |
| comprendre l'architecture d'ensemble, un scénario qualité, un risque | `docs/architecture/` |
| retrouver ou écrire une décision structurante | `docs/architecture/adr/` |
| connaître l'état, les priorités, l'autorité d'un document | `docs/project/governance/` |
| lire le plan d'un jalon | `docs/project/roadmap/` |
| lire la preuve d'un jalon ou d'une release | `docs/project/validation/` |
| lire un audit daté | `docs/project/audits/` |

Une page **mixte** (mode d'emploi et fonctionnement interne) se coupe en deux : `user/` dit comment
s'en servir, `developer/` comment c'est construit.

Une page de `docs/user/` reste **lisible sans le dépôt** : elle parle du produit installé, de ses
commandes et de ses fichiers de configuration. Pas de SHA, de compteur de tests ou de couverture,
de numéro d'issue ou de PR, de commande de build, de chemin `src/`.

## Dossiers facultatifs

Ne créer que ce qui a un contenu, ou un contenu prévu à court terme et confirmé par l'utilisateur.
Un dossier vide n'aide personne et Git ne le suit pas.

| Dossier | À créer quand |
|---|---|
| `user/release-notes/` | l'application publie des versions |
| `developer/reference/` et ses sous-dossiers (`openapi/`, `contracts/`, `domain/`) | le dépôt expose un contrat machine |
| `project/roadmap/`, `project/validation/` | le projet fonctionne par jalons |
| `project/audits/`, `project/product/`, `project/research/` | un audit, un cadrage ou une étude existe |
| `project/rapport-supervisor/` | jamais à la main : le superviseur le crée et l'ignore lui-même |

Les quatre dossiers de premier niveau et `docs/README.md` sont toujours créés, avec leur
`README.md` d'index.

## Ce qui reste hors de `docs/`

Un fichier lu par un outil ou attendu à un emplacement conventionnel ne bouge pas :
`README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `LICENSE` à la racine ; les
`README.md` de sous-dossiers de code (`scripts/README.md`) ; un contrat lu par le build. `.archgate/`
porte la configuration d'Archgate, pas de documentation. `openspec/` reste à sa place.

## Relevés datés

Plans d'exécution, `VALIDATION_*`, audits, études, notes de version, changements OpenSpec archivés
sont des relevés datés. Lors d'un déplacement, leurs **liens** sont recalculés, leur **prose** n'est
pas réécrite : elle cite les chemins de sa date. La table de correspondance entre anciens et
nouveaux chemins vit dans `docs/project/README.md`.

Nommage : audit `AUDIT_<objet>_<AAAA-MM-JJ>.md`, ou dossier `<AAAA-MM-JJ>/` s'il porte plusieurs
fichiers ; notes de version `RELEASE_NOTES_<version>.md`.

## Anciens emplacements courants

À ranger lors de la migration, puis interdits par la règle :

| Ancien | Nouveau |
|---|---|
| `docs/adr/`, `adr/`, `decisions/`, `.archgate/adrs/*.md` | `docs/architecture/adr/` |
| `docs/arc42/`, `docs/architecture.md` | `docs/architecture/` (skill `arc42-architecture`) |
| `docs/openapi/`, `docs/api/`, `docs/reference/`, `docs/contracts/`, `docs/domain/` | `docs/developer/reference/` |
| `docs/release/`, `docs/releases/` | `docs/user/release-notes/` |
| `docs/governance/`, `docs/roadmap/`, `docs/validation/` | `docs/project/<même nom>/` |
| `docs/audit/`, `docs/audits/` | `docs/project/audits/` |
| `docs/product/`, `docs/research/` | `docs/project/<même nom>/` |
| `docs/rapport-supervisor/` | `docs/project/rapport-supervisor/` (réglage du superviseur, pas un déplacement de fichiers) |
| `docs/*.md` en vrac | selon le lecteur (tableau ci-dessus) |
