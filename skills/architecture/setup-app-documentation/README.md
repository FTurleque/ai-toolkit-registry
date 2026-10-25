# Mise en place de la documentation d'une application

> Range toute la documentation d'une application dans `docs/`, par lecteur, crée les index et
> l'aiguillage, et installe dans l'application la règle `.claude/rules/documentation.md` qui garde ce
> rangement. Configure Archgate et le superviseur de code s'ils sont installés.

## Ce que ça change

Sans le skill, « range la doc » produit un déplacement ponctuel, sans règle pour la suite : six
mois plus tard, un second dossier d'ADR apparaît et les pages utilisateur citent des SHA. Avec lui :

- **Une arborescence par lecteur** : `user/` (utiliser), `developer/` (construire),
  `architecture/` (comprendre et décider), `project/` (piloter et auditer). `docs/README.md` est un
  simple aiguillage ; chaque dossier a son index.
- **Audit et plan d'abord.** Inventaire, chemins cités par le code, les tests ou la CI, outils
  détectés, plan de rangement fichier par fichier. Rien ne bouge avant validation.
- **Des déplacements qui ne cassent rien** : `git mv`, citations mises à jour, liens recalculés,
  table de correspondance des anciens chemins dans `docs/project/README.md`. La prose des relevés
  datés (audits, validations, notes de version) n'est pas réécrite.
- **Un seul registre d'ADR**, `docs/architecture/adr/`, au format Archgate. Le contenu de
  `docs/architecture/` est délégué au skill [`arc42-architecture`](../arc42-architecture/README.md).
- **Archgate, s'il est installé** (`archgate --version`) : `.archgate/config.json` pointe sur
  `docs/architecture/adr/` (`paths.adrs`), sans `archgate init`. Absent : signalé, rien n'est écrit
  sous `.archgate/`.
- **Superviseur de code, s'il est installé** (plugin `code-supervisor` ou hook `supervisor.py`) :
  `.claude/supervisor.config.json` place rapports et état sous `docs/project/rapport-supervisor/`,
  et les relevés datés ne sont pas relus. Absent : signalé, rien n'est écrit.
- **Une règle qui dure** : `.claude/rules/documentation.md` dit où ranger chaque nouveau fichier, ce
  qui est interdit, et comment déplacer une page sans casser ses citations.
- **Un contrôle outillé** : `resources/check_docs.py` signale un fichier à la racine de `docs/`, un
  dossier de premier niveau imprévu, un lien relatif cassé, un `.md` non-ADR dans le registre, un `id`
  d'ADR différent du nom de fichier, une ADR restée dans `.archgate/adrs/`, une page absente de son
  index, une page utilisateur qui cite `src/`, une commande de build ou un SHA.

## Installation

| Surface | Emplacement | Vérifié |
|---------|-------------|---------|
| Claude Code, portée utilisateur | `~/.claude/skills/setup-app-documentation/` | installation oui (Windows 10) ; déclenchement automatique pas encore observé |
| Claude Code, portée projet | `<projet>/.claude/skills/setup-app-documentation/` | non vérifié |

```bash
python tools/install_skill.py install setup-app-documentation arc42-architecture
```

Installer aussi `arc42-architecture`, auquel ce skill délègue `docs/architecture/`. Python 3.8+
n'est nécessaire que pour `check_docs.py`. Voir [docs/install.md](../../../docs/install.md).

## Usage

```text
/setup-app-documentation mets en place la documentation de ce dépôt
/setup-app-documentation audite seulement l'organisation de docs/
range la doc, on a des ADR dans docs/adr et dans .archgate/adrs
```

Contrôle manuel, depuis la racine de l'application :

```bash
python ~/.claude/skills/setup-app-documentation/resources/check_docs.py --root .
```

Exemple de rapport d'audit : [examples/audit-plan.md](examples/audit-plan.md).

## Limites

- **Pas de rédaction de fond.** Le skill crée la structure, les index et les pages dont le dépôt
  fournit le contenu ; il annonce les autres sous « À écrire » plutôt que de les inventer.
- **Superviseur : `code-supervisor` seulement.** Un autre superviseur est signalé mais pas configuré.
- **Archgate vérifié en 0.60.0.** `paths.adrs` et la détection du projet par `.archgate/lint/` ont été
  constatés sur cette version ; une autre version peut différer.
- **`check_docs.py` voit des formes.** Il ne juge pas qu'une page est rangée chez le bon lecteur ;
  il repère une page utilisateur technique par motifs (`src/`, `mvn`, `npm run`, SHA) et peut se
  tromper. Un index qui regroupe des pages par plage (« M0 → M14 ») sans nommer chaque fichier
  produit des avertissements.
- **Gros dépôts.** L'inventaire et la recherche des citations coûtent cher sur un monorepo : cibler
  une application.
