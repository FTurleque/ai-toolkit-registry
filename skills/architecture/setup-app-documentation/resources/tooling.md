# Archgate et superviseur : détecter, puis configurer

Deux outils facultatifs. Chacun est **détecté** pendant l'audit ; sa configuration n'est écrite
qu'en phase 2, après validation, et seulement s'il est installé. Absent : le signaler avec la
commande d'installation et continuer sans lui.

---

## Archgate

### Détecter

| Vérification | Commande | Lecture |
|---|---|---|
| CLI installé | `archgate --version` | une version : installé. « commande introuvable » : absent |
| Projet déjà configuré | `.archgate/config.json`, `.archgate/adrs/`, `.archgate/lint/` | présent ou non |
| Registre déclaré | clé `paths.adrs` de `.archgate/config.json` | absent : Archgate lit `.archgate/adrs/` |
| ADR reconnus | `archgate adr list` (dans le projet) | identifiants actuels, à comparer après migration |
| Règles exécutées | `archgate check --base HEAD --verbose --output json` sur un arbre propre | noter `total` avant toute migration |

Sous Windows, le premier lancement du binaire npm d'Archgate appelle `powershell` pour le
décompresser : si `C:\Windows\System32\WindowsPowerShell\v1.0` n'est pas dans le `PATH`, il échoue.
Ce n'est pas une absence d'Archgate : le dire et proposer d'ajouter ce dossier au `PATH` du processus.

Absent : `Archgate non installé — ADR rédigés au format Archgate, aucune configuration .archgate/
écrite. Installation : https://cli.archgate.dev`. Ne jamais l'installer soi-même.

### Configurer (installé)

Constaté avec Archgate 0.60.0. Pas besoin de `archgate init`, qui écrit aussi
`.claude/settings.local.json` (agent `archgate:developer`) : ne le lancer que sur demande explicite.

1. `.archgate/config.json` — créer ou compléter, sans toucher aux autres clés :

   ```json
   {
     "domains": {},
     "baseBranch": "<branche de base réelle, ex. origin/main>",
     "paths": { "adrs": "docs/architecture/adr" }
   }
   ```

   `baseBranch` : garder la valeur existante ; à la création, prendre la branche de base réelle du
   dépôt (`git symbolic-ref refs/remotes/origin/HEAD`, sinon la branche par défaut locale).
   Un préfixe hors des domaines intégrés (`ARCH`, `BE`, `FE`, `DATA`, `GEN`) se déclare avec
   `archgate adr domain add <nom> <PRÉFIXE>` (par exemple `security SEC`), qui écrit
   `"domains": { "security": "SEC" }`.

2. `.archgate/lint/` doit exister (un `.gitkeep` suffit) : sans lui ni `.archgate/adrs/`, Archgate ne
   reconnaît pas le projet (`No .archgate/ directory found`).
3. `.gitignore` : `.archgate/rules.d.ts` et `docs/architecture/rules.d.ts` — `check` régénère les deux.
4. ADR présents dans `.archgate/adrs/` : `git mv` vers `docs/architecture/adr/` avec leurs
   `.rules.ts`, dont la référence devient `/// <reference path="../rules.d.ts" />`. Ni `id` ni contenu
   ne changent. Laisser `.archgate/adrs/` vide (ou un `.gitkeep`).
5. Vérifier : `archgate adr list` donne les mêmes identifiants qu'avant, `archgate check` le même
   `total`, et `unparsedAdrs` est vide (aucun `.md` non-ADR dans `adr/`).

### Convertir une ADR d'un autre format

Une ADR acceptée ne se réécrit pas : la convertir, c'est changer sa forme, pas son contenu.

- Nouveau nom `<PRÉFIXE>-<NNN>-<slug>.md` (numéro suivant pour ce préfixe), par `git mv`.
- Front matter `id`, `title` (titre d'origine), `domain`, `rules: false`.
- Le texte d'origine est repris **mot pour mot** sous les intitulés Archgate ; statut et date
  d'origine en tête de `Decision`. Une rubrique du gabarit absente de l'original porte
  `Non déterminé` : ne pas inventer de critères, d'options ni de décideurs.
- Provenance : une ligne `Ancien emplacement : <chemin>` dans `References`, et la table de
  correspondance. Pas de commentaire qui raconte la conversion.

Le format et le nommage des ADR sont ceux du skill `arc42-architecture`
(`resources/templates/adr-template.md`) : `<PRÉFIXE>-<NNN>-<slug>.md`, numéro séquentiel par
préfixe, front matter `id`, `title`, `domain`, `rules`, `files`. Ne pas utiliser
`archgate adr create` pour numéroter sans vérifier le numéro suivant dans le registre.

---

## Superviseur de code

Le superviseur de référence est le plugin `code-supervisor` du registre ai-toolkit-registry. Il
écrit ses rapports et son état dans un sous-dossier de la racine Git (`log_subdir`), qu'il ignore
lui-même dans Git.

### Détecter

L'un des trois suffit :

| Installation | Indice |
|---|---|
| Plugin | `claude plugin list` affiche `code-supervisor@…` activé |
| Manuelle, globale | `~/.claude/settings.json` déclare un hook `Stop` ou `SubagentStop` dont la commande lance `supervisor.py` |
| Manuelle, projet | même hook dans `<projet>/.claude/settings.json` |

Une installation manuelle de `code-supervisor` se reconnaît à `~/.claude/hooks/supervisor.py` et
à son paquet `~/.claude/hooks/supervisor/`. Confirmation : `python ~/.claude/hooks/supervisor.py
--self-test` (ou le même script dans le dossier du plugin) se termine par un succès. Un hook
`supervisor.py` qui ne répond pas à `--self-test` est un autre superviseur.

Un autre superviseur (hook maison) : le signaler et ne configurer que ce que sa documentation
permet. Ne pas lui appliquer les clés de `code-supervisor`.

Absent : `Aucun superviseur de code détecté — pas de dossier de rapports ni de
supervisor.config.json. Installation : claude plugin marketplace add FTurleque/ai-toolkit-registry
puis claude plugin install code-supervisor@ai-toolkit-registry`. Ne jamais l'installer soi-même.

### Configurer (`code-supervisor` installé)

`<projet>/.claude/supervisor.config.json` — créer ou fusionner, sans écraser les autres clés :

```json
{
  "log_subdir": "docs/project/rapport-supervisor",
  "quiet_paths": [
    "docs/project/audits/*",
    "docs/project/validation/*",
    "docs/project/roadmap/*"
  ]
}
```

- `log_subdir` place rapports et état sous `docs/project/`, à la racine Git. Le dossier est créé
  et ignoré par le superviseur : ne pas le créer, ne rien y versionner.
- `quiet_paths` : les relevés datés ne sont pas relus (leur prose ne se réécrit pas). Ne garder que
  les dossiers qui existent.
- Clés interdites dans un projet (ignorées par le superviseur) : `external_tools`, `llm.cli`,
  `log_dir`. Ne pas les écrire.
- Ancien dossier `docs/rapport-supervisor/` : il n'est pas versionné ; le signaler, et proposer de
  le supprimer une fois `log_subdir` en place (suppression de fichiers locaux : demander).
