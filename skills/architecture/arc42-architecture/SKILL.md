---
kind: skill
name: arc42-architecture
displayName: Documentation d'architecture arc42
description: >-
  Audite la conformité d'une application au standard arc42, puis crée, complète ou corrige sa
  documentation d'architecture dans docs/architecture/ : les 12 sections arc42, les diagrammes C4
  (contexte, conteneurs, composants, déploiement) et de séquence en Mermaid, les ADR en Markdown, et
  la règle qui garde les décisions futures conformes. À utiliser dès que la documentation
  d'architecture est en jeu, même sans les mots arc42, C4 ou ADR : documenter, revoir ou
  schématiser l'architecture d'une application, ajouter un service, changer un protocole, tracer une
  décision technique structurante. Trois modes : AUDIT (rapport de conformité, lecture seule),
  INTÉGRATION (création ou complétion de docs/architecture/), MAINTENANCE (documentation et ADR
  tenus à jour). Audite et rend compte d'abord ; n'écrit qu'après validation explicite.
version: 3.0.0
status: experimental
category: architecture
tags:
  - arc42
  - c4
  - adr
  - mermaid
  - documentation
  - architecture
compatibility:
  - claude-code
authors:
  - Fabrice Turleque
license: MIT
---

# Skill `arc42-architecture`

> **But** : Auditer la conformité arc42 d'une application, puis créer ou compléter sa documentation d'architecture (arc42 + C4 + ADR + Mermaid) et installer la règle qui maintient cette conformité.

Skill **générique** — fonctionne dans n'importe quelle application cible (Quarkus/Java, PHP,
front, batch). Aucune technologie n'est codée en dur : tout est **découvert** depuis le dépôt.

Tu agis comme **architecte logiciel senior et rédacteur technique**. Langue de production :
**français**.

**Fichiers embarqués** :

| Fichier | Rôle |
|---|---|
| `./resources/checklists/conformite-arc42.md` | Grille d'audit — critères, verdicts, barème |
| `./resources/templates/arc42-sections.md` | Squelette des 12 sections + `README.md` |
| `./resources/templates/adr-template.md` | Gabarit d'ADR au format Archgate, statuts, configuration Archgate |
| `./resources/templates/mermaid-patterns.md` | Patterns Mermaid — `C4Context`, `C4Container`, `C4Component`, `C4Deployment`, `sequenceDiagram`, `classDiagram` |
| `./resources/templates/rule-arc42.md` | Règle à installer dans `<app>/.claude/rules/` |

---

## 🚦 Règle absolue — auditer avant d'écrire

> **Phase 1 — AUDIT** : inspection du dépôt → grille de conformité → rapport → **ARRÊT**.
> **Phase 2 — INTÉGRATION** : création ou complétion des fichiers, uniquement après validation
> explicite de l'utilisateur.

Confirmations acceptées : « OK », « Go », « Validé », « Lance l'intégration », ou toute approbation
claire. Une description, un contexte ou le silence ne constituent **pas** une confirmation.

Exception : si l'utilisateur demande explicitement l'audit **seul** (« audite », « vérifie la
conformité »), s'arrêter au rapport et ne rien écrire.

---

## 🎯 Les trois modes

| Mode | Déclencheur | Écrit des fichiers |
|---|---|---|
| **AUDIT** | « vérifier / auditer la conformité arc42 » | ❌ Jamais |
| **INTÉGRATION** | « mettre en place / compléter / corriger arc42 » | ✅ Après validation |
| **MAINTENANCE** | Une décision d'architecture vient d'être prise ou un composant a changé | ✅ Ciblé, sections impactées + ADR |

En cas de doute : commencer par **AUDIT**. Le rapport détermine le mode réellement utile.

---

## 📁 Structure cible

```
docs/architecture/
├── README.md
├── arc42/
│   ├── 01-introduction-objectifs.md
│   ├── 02-contraintes.md
│   ├── 03-contexte-perimetre.md
│   ├── 04-strategie-solution.md
│   ├── 05-vue-blocs.md
│   ├── 06-vue-execution.md
│   ├── 07-vue-deploiement.md
│   ├── 08-concepts-transverses.md
│   ├── 09-decisions.md
│   ├── 10-exigences-qualite.md
│   ├── 11-risques-dette.md
│   └── 12-glossaire.md
├── adr/                   # ADR au format Archgate, et rien d'autre (index : arc42/09)
│   ├── ARCH-001-<slug>.md
│   └── ARCH-001-<slug>.rules.ts   # seulement si une règle automatisée existe
├── diagrams/              # diagrammes autonomes (.mmd) réutilisés par plusieurs sections
├── quality/
│   └── scenarios.md
└── risks/
    └── register.md
```

`docs/architecture/adr/` est **le** registre de décisions de l'application, pour arc42 comme pour
Archgate : Archgate y est pointé par `paths.adrs` dans `.archgate/config.json` (détail et pièges
constatés : `./resources/templates/adr-template.md`, section « Configuration Archgate »).

**Structure existante divergente** : ne pas la détruire. Le rapport d'audit propose un plan de
migration (renommages, fusions, redirections) que l'utilisateur arbitre avant exécution.

---

## 🔍 Phase 1 — AUDIT

### Étape 1 · Inspecter le dépôt

Balayer, dans cet ordre, et **noter le chemin exact de chaque preuve** :

| Source | Ce qu'on y cherche |
|---|---|
| `README.md`, `CLAUDE.md`, `.claude/rules/*.md` | Mission, périmètre, contraintes déjà écrites |
| Manifests (`pom.xml`, `package.json`, `composer.json`, `*.csproj`) | Langages, frameworks, modules, dépendances structurantes |
| `docs/`, wiki, `*.adoc`, `*.puml`, `*.drawio` | Documentation d'architecture préexistante, sous quelque forme |
| ADR existants (`docs/adr/`, `adr/`, `decisions/`, `.archgate/adrs/`) | Décisions déjà tracées, statuts |
| `.archgate/config.json` (clé `paths.adrs`), `*.rules.ts` ; `archgate adr list` si le CLI est installé | Archgate utilisé ? Pointe-t-il déjà sur `docs/architecture/adr/` ? |
| `Dockerfile`, `docker-compose*`, `k8s/`, Helm, Terraform, Ansible | Nœuds, conteneurs, réseaux, environnements |
| CI/CD (`.gitlab-ci.yml`, `Jenkinsfile`, `.github/workflows/`) | Étapes de build, tests, promotion, rollback |
| Config (`application*.properties/yaml`, `.env.template`) | Systèmes externes, protocoles, stockages, secrets attendus |
| Schémas de données (`*.sql`, migrations Liquibase/Flyway, entités) | Persistance, modèle |
| Contrats d'API (`openapi*.yaml`, `*.proto`, WSDL, contrôleurs) | Interfaces exposées et consommées |
| Arborescence des sources | Style de décomposition réel (couches, modules, hexagonal…) |
| Tests | Niveaux de test, ce qui est réellement vérifié |
| Historique Git | Zones instables, refactorings, dette |

### Étape 2 · Renseigner la fiche de contexte

Remplir chaque entrée avec sa **preuve** ou avec `Non déterminé` :

```
- Nom :
- Mission métier :
- Utilisateurs :
- Langages et frameworks :
- Dépôts ou modules :
- Systèmes externes :
- Stockages :
- Protocoles :
- Plateformes de déploiement :
- Contraintes réglementaires :
- Contraintes organisationnelles :
- Objectifs qualité connus :
- Documentation existante :
- ADR existants :
- Environnements :
- Zones d'incertitude :
```

### Étape 3 · Appliquer la grille

Grille complète : `./resources/checklists/conformite-arc42.md`.

Verdict par section, avec **une preuve ou une absence de preuve** à l'appui :

| Verdict | Signification |
|---|---|
| ✅ **Conforme** | Section présente, structurée arc42, cohérente avec le code observé |
| 🟡 **Partiel** | Section présente mais incomplète (diagramme manquant, scénario absent, contenu vide) |
| ⚠️ **Divergent** | Section présente mais **contredite par le dépôt** (composant disparu, protocole faux, nœud inexistant) |
| ❌ **Absent** | Aucune trace |
| ➖ **Non applicable** | Justifier explicitement pourquoi |

⚠️ **Divergent est le verdict le plus grave** : une documentation fausse coûte plus qu'une
documentation absente. Toujours le remonter avant les sections `Absent`.

### Étape 4 · Produire le rapport d'audit

```markdown
## Audit de conformité arc42 — {application}

### Fiche de contexte
{fiche renseignée, chaque valeur suivie de sa preuve ou de « Non déterminé »}

### Verdict global
Conformité : {n}/12 sections conformes — {n} partielles, {n} divergentes, {n} absentes
Outillage : arc42 {oui/non} · C4 {oui/non} · ADR {oui/non} · Mermaid {oui/non}

### Détail par section
| # | Section | Verdict | Preuve / manque | Fichiers concernés |
|---|---------|---------|-----------------|--------------------|
| 1 | Introduction et objectifs | 🟡 | Mission dans README, aucun objectif qualité priorisé | README.md:12 |
| … | | | | |

### Incohérences code ↔ déploiement ↔ documentation
{liste ordonnée par gravité, chaque ligne avec les deux sources qui se contredisent}

### Hypothèses à valider
| Hypothèse | Preuve nécessaire | Qui peut trancher |
|---|---|---|

### Questions ouvertes
{questions qui bloquent la production d'une section}

### ADR à créer
{décisions structurantes visibles dans le code mais non tracées}

### Scénarios qualité manquants
{qualités citées sans scénario mesurable}

### Plan de migration priorisé
| # | Action | Effort | Gain | Prérequis |
|---|--------|--------|------|-----------|

### Contrôles CI recommandés
{cf. section « Contrôles CI » du skill}
```

Conclure par :

> **Prêt à intégrer / compléter la documentation arc42. Confirmez pour continuer (Phase 2).**

---

## 🏗️ Phase 2 — INTÉGRATION

Après confirmation explicite uniquement. Ordre d'exécution :

1. **Créer l'arborescence** `docs/architecture/` manquante — ne jamais écraser un fichier existant
   sans annoncer précisément ce qui est remplacé.
2. **Rédiger dans cet ordre de dépendance** : 03 (contexte) → 05 (blocs) → 06 (exécution) →
   07 (déploiement) → 01, 02, 04, 08, 10, 11, 12 → 09 (index ADR, en dernier).
   Le contexte fixe les noms ; toutes les autres sections les réutilisent **à l'identique**.
3. **Aligner Archgate** s'il est utilisé (`.archgate/` présent) : ajouter
   `"paths": { "adrs": "docs/architecture/adr" }` à `.archgate/config.json`, garder
   `.archgate/lint/`, ignorer `.archgate/rules.d.ts` et `docs/architecture/rules.d.ts` dans
   `.gitignore`. ADR déjà présents dans `.archgate/adrs/` : les **déplacer** (avec leurs `.rules.ts`,
   dont la référence devient `/// <reference path="../rules.d.ts" />`), sans changer leur `id` ni
   leur contenu, puis vérifier que `archgate adr list` les liste tous et que `archgate check` exécute
   le même nombre de règles qu'avant. ADR dans un autre format (`docs/adr/0003-….md`) : plan de
   conversion dans le rapport, exécuté après validation. Ne jamais lancer `archgate init` sans
   demande explicite.
4. **Créer les ADR** identifiés à l'audit depuis `./resources/templates/adr-template.md` — un par
   décision, jamais un ADR fourre-tout. Aucun `README.md` ni `template.md` dans `adr/`.
5. **Remplir `quality/scenarios.md` et `risks/register.md`** — sections 10 et 11 y renvoient
   plutôt que de dupliquer.
6. **Installer la règle** `<app>/.claude/rules/arc42-architecture.md` depuis
   `./resources/templates/rule-arc42.md` :
   - fichier absent → le créer tel quel, `LastUpdate` = date du jour ;
   - fichier présent → comparer, proposer une fusion, **ne pas écraser silencieusement** ;
   - adapter le seul point variable : le chemin réel de `docs/architecture/` si l'application
     l'héberge ailleurs.
7. **Référencer** la documentation depuis le `README.md` racine et le `CLAUDE.md` de l'application
   — sinon personne ne la trouve et Claude ne la charge pas.
8. **Vérifier** : cf. « Vérifications de sortie ».

### Contenu attendu par section

Détail complet et squelettes : `./resources/templates/arc42-sections.md`. Exigences non négociables :

| # | Section | Doit contenir |
|---|---|---|
| 1 | Introduction et objectifs | Résumé du système, objectifs métier, parties prenantes, **3 à 5 objectifs qualité priorisés** |
| 2 | Contraintes | Contraintes métier / techniques / réglementaires / organisationnelles, avec **distinction contrainte imposée vs préférence** |
| 3 | Contexte et périmètre | Frontière du système, acteurs, systèmes externes, interfaces, **diagramme `C4Context`** |
| 4 | Stratégie de solution | Principes, style de décomposition, technologies structurantes, mécanismes servant les objectifs qualité, **liens vers les ADR** |
| 5 | Vue des blocs | **`C4Container`**, `C4Component` pour les conteneurs complexes uniquement, `classDiagram` pour les zones critiques ; par bloc : responsabilité, interfaces, dépendances, **chemin du code source** |
| 6 | Vue d'exécution | **≥ 1 scénario nominal, 1 scénario d'erreur, 1 scénario d'exploitation** (démarrage / reprise), en `sequenceDiagram`, noms strictement identiques à la section 5 |
| 7 | Vue de déploiement | Environnements, nœuds, zones réseau, instances, conteneurs, stockages, protocoles, **diagramme `C4Deployment`** |
| 8 | Concepts transverses | Identité et accès · sécurité · données · interfaces et versionnement · erreurs · résilience · configuration · observabilité · persistance · messaging · performance · concurrence · tests · déploiement et rollback |
| 9 | Décisions | **Index seul** : identifiant, titre, statut, date, relation de remplacement. Ne jamais recopier un ADR |
| 10 | Exigences qualité | Tableau des qualités + scénarios d'usage / de changement / de défaillance, chacun avec **stimulus, environnement, réponse, mesure, seuil, méthode de vérification, propriétaire** |
| 11 | Risques et dette | Priorisés, avec **probabilité, impact, exposition, mitigation, propriétaire, date cible** |
| 12 | Glossaire | Termes métier, termes techniques, acronymes ambigus |

### Entête de version

Chaque fichier produit porte l'entête du dépôt cible s'il en impose une, par exemple :

```markdown
> **Version** : 1.0.0  
> **LastUpdate** : AAAA-MM-JJ  
> **But** : Phrase unique décrivant ce que ce fichier sert à faire.
```

Les deux espaces en fin des lignes `Version` et `LastUpdate` sont obligatoires.

---

## 🔄 Mode MAINTENANCE

Déclencheurs — dès qu'un de ces événements survient, la documentation est **à mettre à jour dans
le même changement**, pas plus tard :

| Événement | Sections à toucher |
|---|---|
| Nouveau conteneur, service, module | 05, 07, + ADR si le choix est structurant |
| Nouveau système externe ou nouvelle interface | 03, 05, 08 |
| Changement de protocole ou de contrat d'API | 03, 06, 08, + ADR |
| Changement de stockage ou de schéma | 05, 07, 08 |
| Nouvel environnement, changement de topologie | 07 |
| Nouvelle exigence de performance, sécurité, dispo | 01, 10, `quality/scenarios.md` |
| Dette identifiée ou contournement assumé | 11, `risks/register.md` |
| Décision remplaçant une décision antérieure | Nouvel ADR + ancien passé à « Remplacé » + index 09 |

Procédure : identifier les sections impactées → mettre à jour **les diagrammes en même temps que le
texte** → incrémenter `Version` / `LastUpdate` des fichiers touchés → vérifier que les noms restent
cohérents entre sections 3, 5, 6 et 7.

Un diagramme non mis à jour est une **divergence**, c'est-à-dire le pire état possible.

---

## 🧭 Règles de vérité

- **Ne jamais présenter une hypothèse comme un fait.**
- Information non confirmée → `Hypothèse à valider` + **la preuve nécessaire** pour la confirmer.
- Information absente → `Non déterminé`. Jamais de valeur plausible inventée.
- **N'inventer ni composant, ni protocole, ni objectif qualité, ni justification historique.**
- Une justification historique (« ce choix a été fait pour… ») n'est écrite que si elle est
  **sourcée** : ADR, commit, ticket, ou déclaration de l'utilisateur.
- Privilégier l'exactitude à la quantité. Une section courte et vraie vaut mieux qu'une section
  complète et fausse.

---

## 📐 Règles ADR

Gabarit : `./resources/templates/adr-template.md`.

### Quand créer un ADR

Dès qu'un choix remplit **au moins un** critère :

- il est coûteux à inverser ;
- il modifie une frontière ou une dépendance majeure ;
- il engage une technologie structurante ;
- il répond à un objectif qualité critique ;
- il introduit un risque important ;
- il a nécessité de comparer plusieurs options.

### Contenu obligatoire

Titre · statut · date · contexte · critères · options · décision · conséquences positives,
négatives **et neutres** · méthode de validation · liens vers exigences, scénarios, diagrammes et
tickets.

### Cycle de vie

Statuts : `Proposé` · `Accepté` · `Rejeté` · `Remplacé` · `Déprécié`.

> **Ne jamais supprimer ni réécrire un ADR accepté.** Un changement de décision = un **nouvel**
> ADR, et l'ancien passe à « Remplacé par <ID> ». L'historique des décisions est le seul
> endroit où l'on comprend *pourquoi* le système est ce qu'il est.

### Format

Format Archgate, dans `docs/architecture/adr/` :

- fichier `<PRÉFIXE>-<NNN>-<slug>.md`, préfixe du domaine (`ARCH`, `BE`, `FE`, `DATA`, `GEN` ou
  domaine déclaré), numéro séquentiel par préfixe, jamais réutilisé ;
- front matter `id` (égal au début du nom de fichier), `title`, `domain`, `rules`, et `files` pour
  le périmètre ;
- intitulés de section d'Archgate (`Context`, `Decision`, `Do's and Don'ts`, `Consequences`,
  `Compliance and Enforcement`, `References`), contenu en français ;
- statut et date en tête de `Decision` (`**Statut : Accepté (AAAA-MM-JJ).**`) : le schéma Archgate
  n'a pas de champ pour eux ;
- `rules: true` seulement avec un fichier `.rules.ts` réel, vu en échec sur une violation.

---

## 🖼️ Règles de diagrammes

Patterns prêts à l'emploi : `./resources/templates/mermaid-patterns.md`.

**Notation imposée** — un type de diagramme par vue, jamais d'équivalent bricolé :

| Vue | Type Mermaid |
|---|---|
| arc42 §3 — contexte | `C4Context` |
| arc42 §5 — conteneurs / composants | `C4Container`, `C4Component` |
| arc42 §5.3 — niveau code | `classDiagram` |
| arc42 §6 — exécution | `sequenceDiagram` |
| arc42 §7 — déploiement | `C4Deployment` |

Les stéréotypes sont portés par le **type d'élément C4** (`Person`, `System`, `Container`,
`ContainerDb`, `Component`, `Deployment_Node`), que Mermaid affiche lui-même. `«interface»` et
`«adapter»`, qui n'ont pas d'équivalent C4, s'écrivent en préfixe du libellé ; au niveau code,
`classDiagram` les porte nativement avec la syntaxe `stereotype` entre doubles chevrons.

**Interdits** :
- ❌ diagramme ASCII ;
- ❌ image binaire (PNG, JPG, diagramme exporté) comme **source** de vérité ;
- ❌ C4 reproduit à la main en `flowchart` — notation maison, non reconnaissable ;
- ❌ mélange de plusieurs niveaux C4 sur un même diagramme.

**Obligatoires** :
- tous les diagrammes dans des blocs ` ```mermaid ` **syntaxiquement valides** ;
- type de diagramme en première ligne du bloc, suivi d'un `title` ;
- ordre des paramètres C4 respecté : `Container(alias, "Nom", "Technologie", "Responsabilité")` —
  inverser technologie et responsabilité produit un diagramme valide mais faux ;
- alias identiques d'une vue à l'autre ;
- indiquer le **type et la portée** du diagramme juste au-dessus du bloc ;
- **nom + responsabilité** pour chaque élément ;
- technologie indiquée **seulement si pertinente** architecturalement ;
- chaque relation **libellée par un verbe ou une action** ;
- protocole indiqué quand il est architecturalement significatif ;
- **mêmes noms partout** — sections 3, 5, 6, 7 et ADR ;
- tout diagramme trop dense est **fractionné** en vues focalisées ;
- **aucune couleur indispensable** à la compréhension (accessibilité, impression N&B).

---

## 🔗 Traçabilité

Pour **chaque élément produit** — section, bloc, diagramme, scénario, risque — indiquer :

- les **preuves** observées dans le dépôt (chemin de fichier, ligne si utile) ;
- les **hypothèses** retenues ;
- les **questions ouvertes** ;
- les **risques** associés ;
- les **fichiers source** concernés.

Forme recommandée en fin de section :

```markdown
---
### Traçabilité

| Élément | Preuve | Hypothèse | Question ouverte | Risque |
|---|---|---|---|---|
| Conteneur `api-rh` | `rh-api/pom.xml`, `Dockerfile:1` | — | — | — |
| Cache Redis | `application.properties:42` | Hypothèse à valider : usage en session partagée | Redis est-il mutualisé entre applications ? | Perte de session au redémarrage |

**Fichiers source** : `rh-api/`, `deploy/k8s/api-rh.yaml`
```

---

## ✅ Vérifications de sortie

Avant de clore la Phase 2 :

- [ ] Tous les blocs Mermaid sont syntaxiquement valides (relire chaque bloc ; en cas de doute,
      simplifier le diagramme plutôt que de livrer un bloc cassé).
- [ ] **Rendu C4 vérifié une fois** dans le visualiseur réellement utilisé par l'équipe (GitLab,
      IDE, export), et le constat consigné dans `docs/architecture/README.md`. Mermaid classe les
      diagrammes `C4*` comme expérimentaux : le rendu dépend de la version embarquée. Si le
      visualiseur ne les rend pas, le signaler et faire trancher — ne pas improviser une notation
      de remplacement diagramme par diagramme.
- [ ] Aucun élément nommé différemment entre les sections 3, 5, 6 et 7.
- [ ] Aucun lien mort — chaque `[texte](chemin)` pointe vers un fichier existant.
- [ ] Chaque ADR référencé dans la section 9 existe dans `adr/`, et l'inverse ; `adr/` ne contient
      que des ADR (et leurs `.rules.ts`).
- [ ] Si Archgate est utilisé : `archgate adr list` liste exactement les ADR de `adr/`, et
      `archgate check --output json` ne signale aucun `unparsedAdrs`.
- [ ] Aucun secret, aucune donnée personnelle, aucun identifiant technique réel (mot de passe,
      token, URL interne avec credentials) dans la documentation ou les diagrammes.
- [ ] Chaque affirmation non sourcée porte `Hypothèse à valider` ou `Non déterminé`.
- [ ] Entête `Version / LastUpdate / But` présente sur chaque fichier produit.
- [ ] `.claude/rules/arc42-architecture.md` installé et référencé.

---

## 📤 Rapport de fin

```markdown
## Documentation arc42 — {application}

### Synthèse exécutive
{5 à 10 lignes : état de l'architecture, ce qui est solide, ce qui inquiète, décision attendue}

### Fichiers créés / modifiés
✅ docs/architecture/arc42/… ({n} fichiers)
✅ docs/architecture/adr/ARCH-001-… ({n} ADR)
✏️ .archgate/config.json — `paths.adrs` (si Archgate est utilisé)
✅ .claude/rules/arc42-architecture.md
✏️ README.md — lien ajouté vers la documentation d'architecture

### Checklist de complétude
| Section | État | Reste à faire |
|---|---|---|

### ADR à créer (non encore rédigés)
### Scénarios qualité manquants
### Incohérences détectées entre code, déploiement et documentation
### Plan de migration priorisé
### Contrôles CI recommandés
```

---

## 🛡️ Contrôles CI recommandés

À proposer dans le rapport, **jamais à installer sans demande explicite** :

| Contrôle | Ce qu'il empêche |
|---|---|
| Validation de la syntaxe Mermaid (`mmdc --validate` ou équivalent) | Diagrammes cassés en production |
| Vérification des liens Markdown internes | Liens morts après un renommage |
| Présence des 12 fichiers `arc42/` | Suppression accidentelle d'une section |
| Numérotation ADR unique et séquentielle par préfixe, `id` égal au nom de fichier | Deux ARCH-007 |
| `archgate check --strict` (si Archgate est utilisé) | Un fichier non-ADR dans `adr/`, une règle en échec |
| Aucun ADR `Accepté` supprimé (diff sur `adr/`) | Perte d'historique de décision |
| Entête `Version / LastUpdate / But` sur chaque `.md` touché | Documentation non datée |
| Rappel de mise à jour si un `Dockerfile`, un manifeste k8s ou un contrat d'API change sans `docs/architecture/` | Divergence code ↔ documentation |

---

## 🔎 Voir aussi

- `./resources/templates/rule-arc42.md` — la règle installée dans l'application cible, qui maintient la
  conformité arc42 dans les décisions futures.
- Skill `generate-uml-diagrams` — diagrammes UML d'un module dans `docs/diagrams/`, hors du dossier
  arc42.
- Skills `adr-author`, `adr-audit`, `adr-check` — pertinence, audit et contrôle des ADR. Ils
  travaillent sur le même registre : celui que désigne `paths.adrs` dans `.archgate/config.json`.
