# Documentation d'architecture arc42

> Audite la documentation d'architecture d'une application au regard d'arc42, puis la crée ou la
> complète dans `docs/architecture/` (12 sections arc42, vues C4 et séquences en Mermaid, ADR), et
> installe la règle qui la garde à jour.

## Ce que ça change

Sans le skill, une demande « documente l'architecture » produit un texte libre, souvent plausible
plutôt que vrai, sans structure stable ni lien avec les décisions. Avec lui :

- **Audit d'abord, écriture ensuite.** La phase 1 inspecte le dépôt (manifestes, déploiement, CI,
  configuration, contrats d'API, documentation existante) et rend un verdict par section arc42 :
  conforme, partiel, divergent, absent ou non applicable, chaque verdict appuyé sur une preuve. Rien
  n'est écrit avant une validation explicite.
- **Le divergent passe avant l'absent.** Une documentation contredite par le code est remontée en
  premier : elle coûte plus cher qu'une documentation manquante.
- **Une structure prévisible** : `docs/architecture/arc42/01-…` à `12-…`, `adr/`, `diagrams/`,
  `quality/scenarios.md`, `risks/register.md`. Une structure existante divergente n'est pas
  détruite : le rapport propose un plan de migration.
- **Une notation imposée par vue** : `C4Context` (§3), `C4Container` et `C4Component` (§5),
  `sequenceDiagram` (§6), `C4Deployment` (§7), `classDiagram` pour le niveau code. Mêmes noms et
  mêmes alias d'une vue à l'autre.
- **Rien d'inventé** : toute information non prouvée porte `Hypothèse à valider` ou
  `Non déterminé`, et chaque section se termine par un tableau de traçabilité.
- **La conformité dure** : le mode MAINTENANCE dit quelles sections toucher selon le changement, et
  la règle `.claude/rules/arc42-architecture.md` installée dans l'application le rappelle.

| Mode | Déclencheur | Écrit des fichiers |
|---|---|---|
| AUDIT | « audite / vérifie la conformité arc42 » | jamais |
| INTÉGRATION | « mets en place / complète / corrige arc42 » | après validation |
| MAINTENANCE | une décision ou un composant vient de changer | ciblé : sections touchées et ADR |

Fichiers embarqués : `resources/checklists/conformite-arc42.md` (grille d'audit),
`resources/templates/arc42-sections.md` (squelette des 12 sections), `adr-template.md`,
`mermaid-patterns.md`, `rule-arc42.md` (règle à installer dans l'application cible).

## Installation

| Surface | Emplacement | Vérifié |
|---------|-------------|---------|
| Claude Code, portée utilisateur | `~/.claude/skills/arc42-architecture/` | installation oui (Windows 10) ; déclenchement automatique pas encore observé |
| Claude Code, portée projet | `<projet>/.claude/skills/arc42-architecture/` | non vérifié |

```bash
python tools/install_skill.py install arc42-architecture
```

L'installateur copie le dossier dans `~/.claude/skills/` (sous Windows, `~` est `%USERPROFILE%`).
Voir [docs/install.md](../../../docs/install.md).

## Usage

Déclenchement automatique sur une demande qui touche à la documentation d'architecture d'une
application ; ou explicite :

```text
/arc42-architecture audite la conformité arc42 de ce dépôt
/arc42-architecture mets en place la documentation arc42
/arc42-architecture on ajoute un service de notification : mets la documentation à jour
```

Exemple de rapport d'audit (application fictive) :
[examples/audit-report.md](examples/audit-report.md).

## Limites

- **Recouvrement avec `generate-uml-diagrams`**, qui se déclenche aussi sur « documente
  l'architecture » et écrit dans `docs/diagrams/`, hors du dossier arc42.
- **Archgate doit être aligné.** `docs/architecture/adr/` est le seul registre d'ADR : il est au
  format Archgate, et Archgate le lit grâce à `paths.adrs` dans `.archgate/config.json`
  (vérifié avec Archgate 0.60.0). Un `README.md` ou un `template.md` dans ce dossier fait échouer
  `archgate check --strict`. Un registre existant dans `.archgate/adrs/` ou `docs/adr/` est déplacé
  ou converti sur plan validé, pas automatiquement.
- **Rendu C4 non garanti.** Mermaid classe les diagrammes `C4*` comme expérimentaux : le rendu
  dépend de la version du visualiseur (GitLab, GitHub, IDE). Le skill demande de le vérifier une
  fois et de faire trancher si le rendu échoue.
- **Aucun contrôle outillé livré.** La validité Mermaid, les liens morts et la cohérence des noms
  entre sections sont relus par le modèle, pas vérifiés par un script ; les contrôles CI sont
  seulement recommandés.
- **Gros dépôts.** L'audit balaie de nombreuses sources ; sur un monorepo, cibler une application
  ou un module.
- **Production en français**, entête `Version / LastUpdate / But` sur chaque fichier produit, même
  si le dépôt cible n'en impose pas.
