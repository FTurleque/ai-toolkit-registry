# Gabarit d'ADR et alignement Archgate

Les ADR vivent dans `docs/architecture/adr/`, au format Archgate : un fichier
`<PRÉFIXE>-<NNN>-<slug>.md` avec front matter, et, si une règle automatisée existe, son compagnon
`<PRÉFIXE>-<NNN>-<slug>.rules.ts`. Le même fichier sert à arc42 et à Archgate : il n'y a qu'un
registre.

Le dossier `adr/` ne contient **que** des ADR. Archgate lit chaque `.md` de ce dossier comme un ADR
et signale les autres (`unparsedAdrs`), ce qui fait échouer `archgate check --strict` : pas de
`README.md` ni de `template.md` dans `adr/`. L'index est la section 9
(`arc42/09-decisions.md`) ; le gabarit reste dans le skill.

---

## Nommage

| Élément | Règle |
|---|---|
| Préfixe | celui du domaine Archgate : `ARCH` (architecture), `BE` (backend), `FE` (frontend), `DATA` (data), `GEN` (general), ou un domaine ajouté par `archgate adr domain add` |
| Numéro | trois chiffres, séquentiel **par préfixe**, jamais réutilisé |
| Slug | kebab-case, en anglais ou dans la langue des noms de fichiers du dépôt |
| Exemple | `ARCH-001-hexagonal-architecture.md`, `DATA-002-postgresql-storage.md` |

Partout ailleurs (sections arc42, index, liens), l'ADR est cité par son `id` : `ARCH-001`.

---

## Gabarit

Les intitulés de section sont ceux d'Archgate ; le contenu est rédigé en français. Le schéma
Archgate n'a ni statut ni date : ils s'écrivent en tête de la section `Decision`.

```markdown
---
id: ARCH-NNN
title: <Titre de la décision, à l'affirmative>
domain: architecture
rules: false
files: ["<motif du périmètre>", "<motif>"]
---

# {Titre de la décision, à l'affirmative}

## Context

{Quel problème se pose, maintenant, et pourquoi il faut trancher. Faits et contraintes
observables uniquement, avec leur source. Ce qui n'est pas confirmé porte « Hypothèse à valider ».}

**Critères de décision :**

| # | Critère | Poids | Pourquoi il compte |
|---|---|---|---|
| 1 | | | |

**Options envisagées :**

- **Option A — {nom}** : description, avantages, inconvénients, coût de sortie.
- **Option B — {nom}** : …
- **Ne rien faire** : toujours évalué. C'est l'option qui gagne par défaut si personne ne décide.

| Critère | Option A | Option B | Ne rien faire |
|---|---|---|---|

## Decision

**Statut : Proposé (AAAA-MM-JJ).** Décideurs : {noms ou rôles}.

**Option retenue** : {A | B | …}

{Le choix, en termes observables : MUST / MUST NOT. Justification adossée aux critères ci-dessus,
sans justification historique non sourcée.}

Périmètre : {modules et dossiers concernés}. Hors périmètre : {…}.

## Do's and Don'ts

### Do
- {…}

### Don't
- {…}

## Consequences

### Positive
- {…}

### Negative
- {…}

### Neutral
- {Ce qui change sans être ni un gain ni une perte : nouvelle dépendance, nouveau vocabulaire,
  nouveau rituel d'équipe. Les omettre donne une décision qui a l'air gratuite.}

### Risks
- {…}

## Compliance and Enforcement

### Automated Enforcement
- {Règle Archgate (`rules: true` et fichier `.rules.ts`), test ArchUnit, contrôle CI : chemin et
  commande. « Aucun » si rien n'existe.}

### Manual Enforcement
- {Ce que la revue humaine vérifie.}

### Validation de la décision
- Comment on saura que la décision est bonne : {…}
- Mesure / indicateur : {…}
- Échéance de revue : {…}
- Condition de remise en cause : {…}

## References

- Exigence : §{section arc42}
- Scénario qualité : [QS-NN](../quality/scenarios.md#qs-nn)
- Diagramme : §{section} ou `../diagrams/{fichier}.mmd`
- Risque : [R-NN](../risks/register.md#r-nn)
- Ticket : {URL ou identifiant}
- Code : `{chemin}`
- Remplace : — | {ID et lien} · Remplacé par : — | {ID et lien}
```

Le front matter est du YAML : un `title` qui commence par `{` ou `[` y devient un objet ou une
liste, et Archgate classe le fichier dans `unparsedAdrs`. Écrire le titre en clair, ou entre
guillemets s'il contient `: ` ou commence par un caractère spécial.

`rules: true` seulement quand le fichier `.rules.ts` existe et qu'on l'a vu échouer sur une
violation. Sans champ `files`, l'ADR s'applique à tout le dépôt.

---

## Statuts

| Statut | Signification |
|---|---|
| `Proposé` | Rédigé, en attente d'arbitrage |
| `Accepté` | En vigueur |
| `Rejeté` | Écarté — l'ADR reste dans le dépôt, la justification reste utile |
| `Remplacé` | Une décision plus récente s'applique (voir « Remplacé par ») |
| `Déprécié` | Sans objet — le contexte a disparu, aucune décision de remplacement |

Un changement de statut met à jour la ligne `**Statut : …**` de l'ADR **et** l'index de la
section 9.

---

## Configuration Archgate

Archgate cherche ses ADR dans `.archgate/adrs/` par défaut. Pour qu'il lise
`docs/architecture/adr/`, `.archgate/config.json` déclare le chemin :

```json
{
  "domains": {},
  "baseBranch": "origin/main",
  "paths": { "adrs": "docs/architecture/adr" }
}
```

Constaté avec Archgate 0.60.0 :

- Le projet n'est reconnu que si `.archgate/adrs/` **ou** `.archgate/lint/` existe : garder
  `.archgate/lint/` (créé par `archgate init`) même quand `.archgate/adrs/` disparaît.
- `archgate check` régénère `rules.d.ts` dans `.archgate/` **et** dans `docs/architecture/` (le
  dossier parent des ADR). Ignorer les deux dans `.gitignore` :
  `.archgate/rules.d.ts` et `docs/architecture/rules.d.ts`.
- Un fichier de règles placé dans `docs/architecture/adr/` référence ce second fichier :
  `/// <reference path="../rules.d.ts" />`.
- `archgate adr list`, `adr show` et `check` (règles comprises) fonctionnent avec ce chemin.

Le skill ne lance jamais `archgate init` de lui-même : cette commande écrit aussi
`.claude/settings.local.json`. Si Archgate est absent, la documentation arc42 fonctionne sans lui ;
le front matter est inoffensif.
