---
kind: skill
name: generate-uml-diagrams
displayName: Diagrammes UML en Mermaid
description: >-
  Génère un jeu de diagrammes UML pertinent, en Mermaid, pour un module, un sous-module ou
  l'application (vue d'ensemble globale dans docs/diagrams/application/ ; avec le détail de chaque
  module si l'application est demandée en détail), à partir du code réel, et l'écrit dans
  docs/diagrams/<module>/<type>-<sujet>.md. Choisit lui-même les types utiles parmi les 14 types
  UML (classes, séquence, états, activité, cas d'utilisation, composants, déploiement, paquetages…)
  et scinde un diagramme trop chargé en plusieurs. À utiliser dès que l'on demande de documenter,
  expliquer, cartographier, comprendre, reprendre ou présenter un module ou une application, d'en
  décrire l'architecture, les flux ou le modèle, de concevoir une fonctionnalité, ou de préparer un
  onboarding, même sans le mot « diagramme ». À utiliser aussi pour toute demande explicite de
  diagramme, schéma, UML ou Mermaid sur du code. Pas pour un organigramme, une slide ou un dessin
  sans rapport avec un logiciel.
version: 1.0.1
status: experimental
category: architecture
tags:
  - uml
  - mermaid
  - diagrams
  - documentation
  - architecture
compatibility:
  - claude-code
requires:
  - python>=3.8 (facultatif, pour le contrôle de syntaxe)
authors:
  - Fabrice Turleque
license: MIT
---

# Diagrammes UML en Mermaid

Produire, pour un périmètre donné, les diagrammes qui aident vraiment à comprendre le code, et
seulement ceux-là. Ils sont écrits en Mermaid dans des fichiers Markdown versionnés avec le code :
GitHub, GitLab et les IDE les affichent sans outil supplémentaire, et un diff montre ce qui a changé.

Un diagramme faux est pire qu'une absence de diagramme : il enseigne une architecture qui n'existe
pas. Tout ce qui est dessiné vient donc du code lu, ou est marqué comme hypothèse.

Référence détaillée des types, signaux, squelettes et pièges : `resources/diagram-catalog.md`, à
côté de ce fichier (`${CLAUDE_SKILL_DIR}/resources/diagram-catalog.md`). La lire avant de choisir
les diagrammes.

## Déroulé

### 1. Fixer le périmètre

Le périmètre est annoncé dans la demande, le plus souvent un module ou un sous-module.

| La demande vise | Périmètre retenu |
|---|---|
| un module ou un sous-module nommé | ce module seul |
| une classe, un fichier, une fonctionnalité | le module qui les contient ; le dire |
| une fonctionnalité qui traverse plusieurs modules | le module qui porte le point d'entrée ; les autres apparaissent comme participants |
| « l'application », « le projet », « l'architecture de l'appli » | la **vue d'ensemble** de l'application, seule |
| « l'application en détail », « détaillée », « complète », « tous les modules », « module par module » | la vue d'ensemble, puis **tous les modules**, traités un par un |
| rien d'identifiable | poser une seule question, en proposant la liste des modules détectés |

Une demande qui vise l'application sans demander le détail reçoit la vue d'ensemble seule ; le
rapport final liste alors les modules détectés, pour que l'utilisateur demande le détail de celui
qui l'intéresse, ou de tous.

**Vue d'ensemble de l'application** : le dossier `docs/diagrams/application/` donne une vision
globale, et seulement elle. Ses éléments sont des modules, des conteneurs, des systèmes externes et
des acteurs, jamais des classes, des méthodes ni des tables : le détail se fait dans le dossier de
chaque module. Elle répond à des questions comme « de quels modules l'application est-elle faite et
qui dépend de qui ? », « où tourne-t-elle ? », « quel module intervient dans un parcours qui en
traverse plusieurs ? ». Diagrammes typiques : `component` des modules et de leurs dépendances
externes, `deployment` (compose, Kubernetes, Terraform), `usecase` des acteurs face aux modules,
`sequence` d'un parcours transverse dont les participants sont des modules. Sa section « Lecture »
renvoie aux dossiers de module pour le détail.

Ce qui couvre toute l'application (fichier de déploiement, carte des modules) relève de cette vue
même quand la demande ne vise qu'un module : ne pas le dessiner dans le dossier du module, et
signaler dans le rapport qu'il appartient à la vue d'ensemble. Si un module s'appelle déjà
`application`, nommer la vue d'ensemble `application-overview`.

**Repérer les modules** : déclarations du build d'abord (`<modules>` d'un `pom.xml`, `include` de
`settings.gradle`, `workspaces` d'un `package.json`, `pnpm-workspace.yaml`, projets d'un `.sln`,
`members` d'un `Cargo.toml`, `go.work`), puis paquets de premier niveau sous `src/` quand le projet
n'a qu'un seul build. Un sous-module est un module déclaré à l'intérieur d'un autre.

**Nom du dossier** : le nom du module tel qu'il apparaît dans le code, en minuscules et en
kebab-case. Un sous-module se range sous son module parent :
`docs/diagrams/<module>/<sous-module>/`.

### 2. Lire avant de dessiner

Lire, pour le périmètre : les points d'entrée (contrôleurs, handlers, consommateurs, commandes,
jobs), les types du domaine, les services et leurs dépendances, la persistance (entités, migrations,
schéma), la configuration et les fichiers de déploiement, les tests qui décrivent un scénario, et la
documentation existante. Si des outils d'intelligence de code sont disponibles (recherche de
symboles, appelants, dépendances), s'en servir pour suivre les appels au lieu de les deviner.

Ce qui n'a pas été vu dans le code n'est pas dessiné comme un fait. Une relation déduite (nommage,
convention de framework) est signalée dans la section « Lecture » du fichier.

Pour une fonctionnalité qui n'existe pas encore (conception), les diagrammes partent de la
description de la demande et le fichier le dit en tête.

### 3. Choisir les diagrammes

Partir des signaux présents dans le module (table « Signaux dans le code » du catalogue) :

- **Ensemble de départ d'un module ordinaire** : un `component` de contexte, un `class` du domaine,
  un `sequence` du scénario principal.
- **Ajouter** `state`, `activity`, `usecase`, `er`, `deployment`, `package` quand leur signal est
  présent. `communication`, `interaction` et `object` restent rares.
- **Ne pas produire** de diagramme de profil, ni de structure composite ou de temps, sauf demande
  explicite ; dans ce cas, livrer l'approximation décrite au catalogue et dire qu'elle en est une.
- **Chaque diagramme répond à une question** qu'un lecteur se poserait (« que se passe-t-il quand on
  paie une facture ? »). Sans question, pas de diagramme. Un petit module en mérite deux ; un module
  riche peut en demander dix.

**Demande explicite** : si l'utilisateur nomme les diagrammes voulus (« un diagramme de séquence du
paiement »), produire exactement ceux-là. D'autres diagrammes utiles peuvent être suggérés en une
ligne à la fin, sans être écrits.

**Scinder plutôt que surcharger** : au-delà des seuils du catalogue (10 classes, 8 participants ou
25 messages, 15 nœuds, 12 états, 10 entités), découper en plusieurs fichiers du même type, chacun
avec son propre sujet : `class-invoice-domain.md` et `class-billing-services.md`, pas un seul
`class-billing.md` illisible.

### 4. Annoncer le plan, puis écrire

Avant d'écrire, annoncer le plan en quelques lignes : pour chaque fichier, son chemin et la question
à laquelle il répond. Puis écrire sans attendre de validation : l'utilisateur ne veut pas avoir à
piloter chaque étape, et il peut interrompre.

Pour l'application en détail, annoncer d'abord une ligne pour la vue d'ensemble et une ligne par
module (nombre et types de diagrammes). Écrire la vue d'ensemble en premier : elle fixe les noms de
modules que les diagrammes de détail reprennent. Traiter ensuite les modules l'un après l'autre, en
terminant les fichiers d'un module avant de passer au suivant. Un module sans code significatif (configuration seule, ressources) est sauté
et mentionné comme tel.

**Fichiers existants** : lire d'abord `docs/diagrams/<module>/`. Un diagramme de même type et même
sujet est mis à jour en place, sous le même nom. Rien n'est supprimé ; un diagramme existant qui ne
correspond plus au code est signalé dans le rapport final.

### 5. Nommer et structurer chaque fichier

Chemin : `docs/diagrams/<module>/<type>-<sujet>.md`, ou `docs/diagrams/application/<type>-<sujet>.md`
pour la vue d'ensemble.

- `<type>` est le préfixe du catalogue : `class`, `object`, `component`, `deployment`, `package`,
  `usecase`, `activity`, `state`, `sequence`, `communication`, `interaction`, `er`.
- `<sujet>` dit ce que montre ce diagramme précis, en kebab-case ASCII, en deux à cinq mots :
  `sequence-invoice-payment.md`, `state-invoice-lifecycle.md`, `class-invoice-domain.md`. Il est en
  anglais, comme les noms de fichiers d'un code source, sauf si le projet nomme ses fichiers dans
  une autre langue ; le contenu du fichier, lui, suit la langue de la documentation. Il distingue
  les diagrammes de même type. Un suffixe numérique
  (`-1`, `-2`) seulement quand un même sujet a dû être coupé et qu'aucun nom meilleur n'existe.

Contenu de chaque fichier, toujours dans cet ordre :

````markdown
# <Type de diagramme en clair> — <sujet en clair>

> **Module** : `<module>` (ou `application`) · **Type** : <type UML> · **Question** : <la question à laquelle il répond>

```mermaid
<diagramme>
```

## Lecture

- <deux à cinq points : ce qu'il faut remarquer, les conventions de flèches utilisées, les
  approximations (type UML rendu par un `flowchart`), les hypothèses à confirmer>

## Sources

- `<chemin/relatif/du/fichier>` — <éléments repris>
````

Un seul bloc `mermaid` par fichier : un fichier = un diagramme, ce qui garde les noms parlants et
les diffs lisibles. Les libellés visibles suivent la langue de la documentation du projet (le
français par défaut) ; les noms de classes, méthodes, tables et endpoints restent ceux du code. Pas
de date dans le fichier : l'historique Git la porte.

### 6. Écrire du Mermaid qui s'affiche

Les squelettes et la table complète des pièges sont dans le catalogue. L'essentiel :

- `stateDiagram-v2`, jamais `stateDiagram` ; `flowchart`, jamais `graph`.
- Identifiants de nœuds en ASCII, sans espace ; libellés visibles entre guillemets dès qu'ils
  contiennent autre chose que des lettres, chiffres et espaces : `A["payer(montant)"]`.
- Aucun nœud ou état nommé `end` en minuscules.
- Fermer chaque `alt`, `opt`, `loop`, `par`, `subgraph`, `state { }` par son `end` ou son `}`.
- Génériques en `~T~` dans un `classDiagram` ; pas de `;` dans un message de séquence.
- Ni directive `%%{init}%%`, ni `style`, `classDef` ou `click` : GitHub et GitLab les ignorent ou
  les bloquent.
- Libellés courts ; le détail va dans « Lecture ».

### 7. Vérifier

1. Si un outil de validation ou de rendu Mermaid est disponible dans la session, valider chaque
   diagramme avec lui. C'est le seul contrôle qui prouve l'affichage.
2. Lancer le contrôle statique livré avec le skill sur le dossier produit :
   `python ${CLAUDE_SKILL_DIR}/resources/check_mermaid.py docs/diagrams/<module>`. Il vérifie la
   structure des fichiers et repère les pièges courants. Corriger tout ce qu'il signale.
3. Si la CLI Mermaid (`mmdc`) est installée, elle peut servir de rendu réel.

Dire dans le rapport quels contrôles ont été exécutés : un contrôle statique vert ne prouve pas
qu'un diagramme s'affiche.

### 8. Rendre compte

Terminer par un rapport bref :

- les fichiers créés ou mis à jour, groupés par module, chacun avec sa question ;
- les modules ou types écartés, et pourquoi ;
- les hypothèses à faire confirmer ;
- les contrôles exécutés et leur résultat.

Ne pas recopier les diagrammes dans la conversation : ils sont dans les fichiers.

## Limites

- Le skill dessine ce qu'il a lu. Sur un très gros module, il échantillonne par sous-paquet et dit ce
  qui n'est pas couvert.
- Le comportement dynamique (réflexion, injection par configuration, appels générés) peut échapper à
  la lecture : les séquences correspondantes sont marquées comme hypothèses.
- Huit types UML sur quatorze ne sont qu'approchés en Mermaid ; trois ne sont pas représentables.
- Les diagrammes ne se mettent pas à jour seuls : relancer le skill sur le module après un
  changement significatif.
