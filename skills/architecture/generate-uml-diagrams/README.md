# Diagrammes UML en Mermaid

> Génère, à partir du code, le jeu de diagrammes UML utile pour un module ou une application, et
> l'écrit en Mermaid dans `docs/diagrams/<module>/`.

## Ce que ça change

Sans le skill, il faut demander chaque diagramme, en préciser le type, et le résultat atterrit dans
la conversation ou dans un fichier fourre-tout. Avec lui :

- **Pas besoin de demander un diagramme.** « Documente le module billing » ou « explique-moi le
  module users, je dois le reprendre » suffit : le skill se déclenche et choisit lui-même les types
  utiles parmi les 14 types UML, d'après ce que le code contient (un statut → un diagramme
  d'états, un point d'entrée qui orchestre plusieurs services → un diagramme de séquence…). C'est
  l'intention de la description du skill ; ce déclenchement n'a pas encore été observé hors des
  essais, où le skill était fourni explicitement.
- **Une demande explicite est respectée à la lettre.** « Un diagramme de séquence du paiement dans
  billing » produit ce diagramme-là, et rien d'autre.
- **Le périmètre est celui de la demande** : un module, un sous-module, ou l'application.
  « L'application » produit une vue d'ensemble globale (modules, déploiement, acteurs, parcours
  transverses, jamais de classe) dans `docs/diagrams/application/`. « L'application en détail »
  ajoute les diagrammes de détail de chaque module, traités un par un.
- **Un fichier par diagramme**, rangé et nommé de façon prévisible :
  `docs/diagrams/<module>/<type>-<sujet>.md` (par exemple `sequence-invoice-payment.md`). Un
  diagramme trop chargé est scindé en plusieurs fichiers du même type.
- **Chaque fichier dit à quelle question il répond** et cite les fichiers sources lus : on sait
  quoi revérifier quand le code change.
- **La syntaxe est contrôlée** : par un outil de rendu Mermaid s'il est disponible, et par
  `resources/check_mermaid.py`, livré avec le skill.

| Type UML | Préfixe | Rendu |
|---|---|---|
| Classes, objets | `class`, `object` | `classDiagram` |
| Séquence | `sequence` | `sequenceDiagram` |
| États-transitions | `state` | `stateDiagram-v2` |
| Activité, cas d'utilisation, composants, déploiement, paquetages, communication, vue d'ensemble des interactions | `activity`, `usecase`, `component`, `deployment`, `package`, `communication`, `interaction` | `flowchart` (approximation) |
| Modèle entité-association (hors UML) | `er` | `erDiagram` |
| Profil, structure composite, temps | — | non produits sauf demande explicite |

## Installation

| Surface | Emplacement | Vérifié |
|---------|-------------|---------|
| Claude Code, portée utilisateur | `~/.claude/skills/generate-uml-diagrams/` | installation oui (Windows 10) ; déclenchement automatique pas encore observé |
| Claude Code, portée projet | `<projet>/.claude/skills/generate-uml-diagrams/` | non vérifié |

```bash
python tools/install_skill.py install generate-uml-diagrams
```

L'installateur copie le dossier dans `~/.claude/skills/` (sous Windows, `~` est `%USERPROFILE%`).
Voir [docs/install.md](../../../docs/install.md). Python 3.8+ n'est nécessaire que pour le contrôle
de syntaxe.

## Usage

Déclenchement automatique sur une demande de documentation, d'explication, de reprise ou de
conception portant sur un module ou une application ; ou explicite :

```text
/generate-uml-diagrams module billing
/generate-uml-diagrams l'application
/generate-uml-diagrams l'application en détail
/generate-uml-diagrams diagramme d'états de la facture dans billing
```

Le skill annonce son plan (un fichier par ligne, avec sa question), écrit les fichiers sans attendre
de validation, les contrôle, puis rend compte : fichiers créés ou mis à jour, types écartés,
hypothèses à confirmer, contrôles exécutés.

Contrôle manuel d'un dossier de diagrammes :

```bash
python ~/.claude/skills/generate-uml-diagrams/resources/check_mermaid.py docs/diagrams/billing
```

Exemple de fichier produit : [examples/billing/sequence-invoice-payment.md](examples/billing/sequence-invoice-payment.md).

## Limites

- **Le skill dessine ce qu'il a lu.** Sur un très gros module, il échantillonne et dit ce qui n'est
  pas couvert ; un appel par réflexion ou par configuration peut lui échapper, et la séquence est
  alors marquée comme hypothèse.
- **Mermaid n'est pas un outil UML** : huit types sont approchés par un `flowchart`, trois ne sont
  pas représentables. L'approximation est signalée dans chaque fichier concerné.
- **`check_mermaid.py` ne fait aucun rendu.** Il écarte les erreurs reconnaissables (blocs non
  fermés, `end` comme nœud, libellés non protégés, mauvais type pour le préfixe…) ; seul un outil de
  rendu prouve l'affichage.
- **Pas de mise à jour automatique** : relancer le skill sur un module après un changement
  significatif. Les diagrammes existants sont mis à jour en place, jamais supprimés.
- **Le choix des diagrammes est un jugement** : il suit les signaux du code et des seuils de
  lisibilité, deux exécutions peuvent différer sur un module limite.
- **Essayé sur un petit projet Maven de test** (trois modules), pas encore sur une application réelle.
- **Surface `claude-code` seule** : le skill lit le code et écrit des fichiers dans le projet.
