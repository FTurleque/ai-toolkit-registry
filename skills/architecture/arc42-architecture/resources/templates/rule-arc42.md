---
applyTo: '**'
description: "Règle d'architecture — toute décision structurante est tracée en ADR et reportée dans la documentation arc42 (C4 + Mermaid) dans le même changement"
---

# 🏛️ Architecture — norme arc42

> **Version** : 1.0.0  
> **LastUpdate** : 2026-08-14  
> **But** : Imposer que toute décision et toute évolution d'architecture soient tracées en ADR et reflétées dans la documentation arc42 du dépôt, dans le même changement.

La documentation d'architecture de cette application suit **arc42**, avec **C4** pour les vues,
**ADR** pour les décisions et **Mermaid** pour tous les diagrammes.

**Source de vérité** : `docs/architecture/`
**Skill de référence** : `arc42-architecture`

### Pourquoi `applyTo: '**'`

La règle ne cible pas un langage : elle se déclenche sur une **nature de changement** — ajouter un
service, changer un protocole, introduire une dépendance structurante — qui peut survenir dans
n'importe quel fichier du dépôt. Un ciblage par extension laisserait passer précisément les
changements les plus structurants (manifeste de déploiement, configuration, contrat d'API).

---

## 1 — Ce qui déclenche une mise à jour

Dès qu'un changement entre dans une de ces catégories, la documentation est mise à jour **dans le
même commit ou la même MR** — pas « plus tard », pas dans un ticket de suivi.

| Changement | À mettre à jour |
|---|---|
| Nouveau conteneur, service, module déployable | `05-vue-blocs.md`, `07-vue-deploiement.md` + ADR |
| Nouveau système externe, nouvelle intégration | `03-contexte-perimetre.md`, `05-vue-blocs.md`, `08-concepts-transverses.md` |
| Changement de protocole ou de contrat d'API | `03`, `06`, `08` + ADR |
| Changement de stockage, de schéma, de stratégie de migration | `05`, `07`, `08` |
| Nouvelle dépendance structurante (framework, broker, cache) | `04-strategie-solution.md` + ADR |
| Nouvel environnement, changement de topologie ou de zone réseau | `07-vue-deploiement.md` |
| Nouvelle exigence de performance, sécurité, disponibilité | `01`, `10-exigences-qualite.md`, `quality/scenarios.md` |
| Contournement assumé, dette acceptée | `11-risques-dette.md`, `risks/register.md` |
| Décision annulant une décision antérieure | Nouvel ADR + ancien passé à `Remplacé` + index `09-decisions.md` |
| Suppression d'un composant | Toutes les sections et diagrammes qui le citent |

**Le diagramme se met à jour en même temps que le texte.** Un diagramme périmé est plus nuisible
qu'un diagramme absent : le lecteur lui fait confiance.

---

## 2 — Quand un ADR est obligatoire

Un ADR est requis dès qu'un choix remplit **au moins un** de ces critères :

- il est coûteux à inverser ;
- il modifie une frontière du système ou une dépendance majeure ;
- il engage une technologie structurante ;
- il répond à un objectif qualité critique ;
- il introduit un risque important ;
- il a nécessité de comparer plusieurs options.

Emplacement : `docs/architecture/adr/<PRÉFIXE>-<NNN>-<slug>.md` (par exemple
`ARCH-001-hexagonal-architecture.md`), au format Archgate : front matter `id`, `title`, `domain`,
`rules`, `files`, et le statut en tête de la section `Decision`. Ce dossier est aussi le registre
Archgate (`paths.adrs` dans `.archgate/config.json`) : il ne contient que des ADR et leurs
fichiers `.rules.ts`, jamais d'index ni de gabarit.

Contenu obligatoire : titre · statut · date · contexte · critères · options · décision ·
conséquences positives, négatives **et** neutres · méthode de validation · liens.

### Règle non négociable

> **Un ADR `Accepté` ne se supprime ni ne se réécrit.** Changer d'avis produit un **nouvel** ADR ;
> l'ancien passe à `Remplacé par <ID>`. L'historique des décisions est le seul endroit où l'on
> comprend pourquoi le système est ce qu'il est — le réécrire efface cette compréhension.

Un ADR `Rejeté` reste également dans le dépôt.

---

## 3 — Règles de diagrammes

**Notation imposée** — un type de diagramme par vue :

| Vue | Type Mermaid |
|---|---|
| §3 contexte | `C4Context` |
| §5 conteneurs / composants | `C4Container`, `C4Component` |
| §5.3 niveau code | `classDiagram` |
| §6 exécution | `sequenceDiagram` |
| §7 déploiement | `C4Deployment` |

Le stéréotype est porté par le type d'élément C4 (`Person`, `System`, `Container`, `ContainerDb`,
`Component`, `Deployment_Node`), affiché par Mermaid. `«interface»` et `«adapter»` s'écrivent en
préfixe du libellé, faute d'équivalent C4.

**Interdits** : diagramme ASCII · image binaire comme source · C4 reproduit à la main en
`flowchart` · mélange de plusieurs niveaux C4 sur un même diagramme.

**Obligatoires** :

- blocs ` ```mermaid ` syntaxiquement valides, type de diagramme en première ligne, puis `title` ;
- ordre des paramètres respecté : `Container(alias, "Nom", "Technologie", "Responsabilité")` ;
- alias identiques d'une vue à l'autre ;
- type et portée annoncés au-dessus du bloc ;
- nom **et** responsabilité pour chaque élément ;
- chaque relation libellée par un verbe ou une action ;
- protocole indiqué quand il est architecturalement significatif ;
- technologie indiquée **seulement** si elle contraint l'architecture ;
- **mêmes noms** dans les sections 3, 5, 6, 7 et dans les ADR ;
- aucune couleur porteuse d'information indispensable ;
- tout diagramme trop dense est fractionné en vues focalisées.

---

## 4 — Règles de vérité

Ces règles s'appliquent à toute production ou mise à jour de documentation d'architecture :

- **Ne jamais présenter une hypothèse comme un fait.**
- Information non confirmée → `Hypothèse à valider`, suivie de la **preuve nécessaire**.
- Information absente → `Non déterminé`. Jamais de valeur plausible inventée.
- **N'inventer ni composant, ni protocole, ni objectif qualité, ni justification historique.**
  Une justification historique n'est écrite que si elle est sourcée : ADR, commit, ticket, ou
  déclaration explicite d'un décideur.
- Chaque élément documenté cite son **fichier source** dans le dépôt.
- L'exactitude passe avant l'exhaustivité : une section courte et vraie vaut mieux qu'une section
  complète et fausse.

---

## 5 — Structure à respecter

```
docs/architecture/
├── README.md
├── arc42/01-introduction-objectifs.md … 12-glossaire.md
├── adr/<PRÉFIXE>-<NNN>-*.md (+ .rules.ts)
├── diagrams/
├── quality/scenarios.md
└── risks/register.md
```

Ne pas créer de documentation d'architecture ailleurs. Deux emplacements = deux sources de vérité
qui divergeront.

---

## 6 — Contrat de sortie attendu de Claude

Lorsqu'un changement d'architecture est demandé ou constaté, annoncer :

1. les sections arc42 impactées ;
2. les ADR à créer ou à passer en `Remplacé` ;
3. les diagrammes à mettre à jour ;
4. les hypothèses retenues et les questions ouvertes ;
5. les incohérences détectées entre code, déploiement et documentation.

Si la mise à jour n'est pas faite dans le même changement, le dire explicitement plutôt que de
laisser croire que la documentation suit.

---

## ✅ Checklist avant commit d'un changement d'architecture

- [ ] Sections arc42 impactées mises à jour
- [ ] Diagrammes Mermaid mis à jour et syntaxiquement valides
- [ ] ADR créé si un des six critères est rempli
- [ ] Ancien ADR passé à `Remplacé` le cas échéant, jamais supprimé
- [ ] Index `09-decisions.md` cohérent avec le contenu de `adr/` (et avec `archgate adr list` si Archgate est utilisé)
- [ ] Noms d'éléments identiques entre sections 3, 5, 6, 7
- [ ] Aucun lien mort
- [ ] Aucun secret ni donnée personnelle dans la documentation ou les diagrammes
- [ ] Hypothèses marquées `Hypothèse à valider`, manques marqués `Non déterminé`
- [ ] Entête `Version / LastUpdate / But` mise à jour sur chaque fichier touché
