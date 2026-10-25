# Squelettes des 12 sections arc42

Gabarits utilisés en **Phase 2 — INTÉGRATION** du skill `arc42-architecture`.

Conventions communes à tous les fichiers produits :

- Entête `Version / LastUpdate / But` après le titre H1 (deux espaces en fin des deux premières
  lignes).
- Tout ce qui n'est pas confirmé par le dépôt porte `Hypothèse à valider` ou `Non déterminé`.
- Bloc `### Traçabilité` en fin de fichier.
- Les noms d'éléments sont identiques d'une section à l'autre.

---

## `README.md` — porte d'entrée

```markdown
# Architecture — {application}

> **Version** : 1.0.0  
> **LastUpdate** : AAAA-MM-JJ  
> **But** : Servir de point d'entrée à la documentation d'architecture arc42 de {application}.

Documentation structurée selon **arc42**, diagrammes en **C4 / UML Mermaid**, décisions tracées
en **ADR**.

## Par où commencer

| Vous voulez | Lisez |
|---|---|
| Comprendre à quoi sert le système | [01 — Introduction et objectifs](arc42/01-introduction-objectifs.md) |
| Savoir avec quoi il dialogue | [03 — Contexte et périmètre](arc42/03-contexte-perimetre.md) |
| Comprendre sa structure interne | [05 — Vue des blocs](arc42/05-vue-blocs.md) |
| Savoir comment il tourne en production | [07 — Vue de déploiement](arc42/07-vue-deploiement.md) |
| Savoir pourquoi un choix a été fait | [09 — Décisions](arc42/09-decisions.md), qui renvoie à chaque ADR de `adr/` |

## Sommaire arc42

1. [Introduction et objectifs](arc42/01-introduction-objectifs.md)
2. [Contraintes](arc42/02-contraintes.md)
3. [Contexte et périmètre](arc42/03-contexte-perimetre.md)
4. [Stratégie de solution](arc42/04-strategie-solution.md)
5. [Vue des blocs de construction](arc42/05-vue-blocs.md)
6. [Vue d'exécution](arc42/06-vue-execution.md)
7. [Vue de déploiement](arc42/07-vue-deploiement.md)
8. [Concepts transverses](arc42/08-concepts-transverses.md)
9. [Décisions](arc42/09-decisions.md)
10. [Exigences qualité](arc42/10-exigences-qualite.md)
11. [Risques et dette technique](arc42/11-risques-dette.md)
12. [Glossaire](arc42/12-glossaire.md)

## Annexes

- [Index des ADR](arc42/09-decisions.md) — les ADR eux-mêmes sont dans `adr/`
- [Scénarios qualité](quality/scenarios.md)
- [Registre des risques](risks/register.md)
- [Diagrammes autonomes](diagrams/)

## Règles de mise à jour

Toute évolution d'architecture met à jour cette documentation **dans le même changement**.
Voir `.claude/rules/arc42-architecture.md`.
```

---

## `01-introduction-objectifs.md`

```markdown
# 1. Introduction et objectifs

> **Version** : 1.0.0  
> **LastUpdate** : AAAA-MM-JJ  
> **But** : Présenter la mission du système, ses parties prenantes et ses objectifs qualité priorisés.

## 1.1 Résumé du système

{3 à 6 phrases. Ce que fait le système, pour qui, et quel problème il résout. Compréhensible sans
connaissance préalable du domaine.}

## 1.2 Objectifs métier

| # | Objectif | Origine | Vérifiable par |
|---|---|---|---|

## 1.3 Parties prenantes

| Partie prenante | Rôle | Attente vis-à-vis de l'architecture |
|---|---|---|

## 1.4 Objectifs qualité priorisés

Trois à cinq maximum. Au-delà, la priorisation n'existe plus.

| Rang | Qualité | Motivation | Scénario de référence |
|---|---|---|---|
| 1 | | | [QS-01](../quality/scenarios.md#qs-01) |

> Chaque qualité listée ici **doit** avoir un mécanisme en section 4 et un scénario mesurable en
> section 10.

### Traçabilité
| Élément | Preuve | Hypothèse | Question ouverte | Risque |
|---|---|---|---|---|
```

---

## `02-contraintes.md`

```markdown
# 2. Contraintes

> **Version** : 1.0.0  
> **LastUpdate** : AAAA-MM-JJ  
> **But** : Recenser ce qui limite les choix d'architecture et distinguer l'imposé du préféré.

## 2.1 Contraintes métier
## 2.2 Contraintes techniques
## 2.3 Contraintes réglementaires
## 2.4 Contraintes organisationnelles

Format commun à chaque sous-section :

| # | Contrainte | Nature | Imposée par | Conséquence architecturale |
|---|---|---|---|---|
| C-01 | | Imposée / Préférence | | |

> **Nature** : `Imposée` = non négociable, une dérogation demande un arbitrage externe.
> `Préférence` = choix d'équipe, révisable par un ADR.
> Confondre les deux fige des choix révisables et fait négocier des choix non négociables.

### Traçabilité
| Élément | Preuve | Hypothèse | Question ouverte | Risque |
|---|---|---|---|---|
```

---

## `03-contexte-perimetre.md`

```markdown
# 3. Contexte et périmètre

> **Version** : 1.0.0  
> **LastUpdate** : AAAA-MM-JJ  
> **But** : Fixer la frontière du système et décrire ses échanges avec les acteurs et systèmes externes.

## 3.1 Frontière du système

**Dans le périmètre** : {liste}
**Hors périmètre** : {liste — aussi important que le précédent}

## 3.2 Diagramme C4 — Niveau 1 · Contexte

**Type** : `C4Context`
**Portée** : {application} et son environnement immédiat

{bloc mermaid — pattern 1 de mermaid-patterns.md}

## 3.3 Contexte métier

| Acteur / Système externe | Stéréotype | Échange | Sens | Données |
|---|---|---|---|---|

## 3.4 Contexte technique

| Interface | Protocole | Format | Authentification | Disponibilité attendue |
|---|---|---|---|---|

### Traçabilité
| Élément | Preuve | Hypothèse | Question ouverte | Risque |
|---|---|---|---|---|
```

---

## `04-strategie-solution.md`

```markdown
# 4. Stratégie de solution

> **Version** : 1.0.0  
> **LastUpdate** : AAAA-MM-JJ  
> **But** : Exposer les principes, le style de décomposition et les mécanismes qui servent les objectifs qualité.

## 4.1 Principes architecturaux

| # | Principe | Conséquence concrète | ADR |
|---|---|---|---|

## 4.2 Style de décomposition

{Nommer le style : couches, hexagonal, modules métier, monolithe modulaire, services…
**Le style annoncé doit correspondre à l'arborescence réelle des sources.** Si le code ne le
respecte pas partout, le dire ici et l'inscrire en section 11.}

## 4.3 Technologies structurantes

| Technologie | Version | Rôle architectural | Coût de sortie | ADR |
|---|---|---|---|---|

## 4.4 Mécanismes par objectif qualité

| Objectif qualité (§1.4) | Mécanisme retenu | Où c'est implémenté | ADR |
|---|---|---|---|

> Un objectif qualité sans ligne dans ce tableau est un vœu, pas un objectif.

### Traçabilité
| Élément | Preuve | Hypothèse | Question ouverte | Risque |
|---|---|---|---|---|
```

---

## `05-vue-blocs.md`

```markdown
# 5. Vue des blocs de construction

> **Version** : 1.0.0  
> **LastUpdate** : AAAA-MM-JJ  
> **But** : Décrire la structure statique du système, de ses conteneurs à ses composants critiques.

## 5.1 Niveau 1 — Conteneurs

**Type** : `C4Container` · **Portée** : {application}

{bloc mermaid — pattern 2 de mermaid-patterns.md}

### Blocs

#### `{nom-du-bloc}`
| | |
|---|---|
| **Stéréotype** | «Container» |
| **Responsabilité** | {une phrase — ce dont ce bloc est seul responsable} |
| **Technologie** | |
| **Interfaces exposées** | |
| **Interfaces consommées** | |
| **Dépendances** | |
| **Code source** | `{chemin réel dans le dépôt}` |

{répéter par bloc}

## 5.2 Niveau 2 — Composants

Uniquement pour les conteneurs dont la complexité interne le justifie. Un conteneur simple n'a pas
besoin d'un diagramme de composants ; en produire un pour la forme dilue l'information.

**Type** : `C4Component` · **Portée** : conteneur `{nom}`

{bloc mermaid — pattern 3 de mermaid-patterns.md}

## 5.3 Niveau 3 — Code (zones critiques uniquement)

**Type** : UML `classDiagram` · **Portée** : {zone}

{bloc mermaid — pattern « classDiagram »}

> Ne documenter au niveau code que ce qui est **critique et stable**. Le reste vieillit plus vite
> que le code.

### Traçabilité
| Élément | Preuve | Hypothèse | Question ouverte | Risque |
|---|---|---|---|---|
```

---

## `06-vue-execution.md`

```markdown
# 6. Vue d'exécution

> **Version** : 1.0.0  
> **LastUpdate** : AAAA-MM-JJ  
> **But** : Montrer comment les blocs collaborent dans le temps, en marche normale, en erreur et en exploitation.

> Les noms d'éléments sont **strictement identiques** à ceux de la section 5.

## 6.1 Scénario nominal — {nom}

**Déclencheur** · **Préconditions** · **Résultat attendu**

{bloc mermaid sequenceDiagram}

## 6.2 Scénario d'erreur — {nom}

**Déclencheur de l'erreur** · **Détection** · **Propagation** · **Effet visible pour l'utilisateur**
· **Journalisation** · **Reprise possible**

{bloc mermaid sequenceDiagram}

## 6.3 Scénario d'exploitation — {démarrage / reprise / bascule / batch}

**Contexte** · **Séquence** · **Point de non-retour** · **Vérification de bonne fin**

{bloc mermaid sequenceDiagram}

### Traçabilité
| Élément | Preuve | Hypothèse | Question ouverte | Risque |
|---|---|---|---|---|
```

---

## `07-vue-deploiement.md`

```markdown
# 7. Vue de déploiement

> **Version** : 1.0.0  
> **LastUpdate** : AAAA-MM-JJ  
> **But** : Décrire l'infrastructure d'exécution, les nœuds, les zones réseau et la façon de déployer et revenir en arrière.

## 7.1 Environnements

| Environnement | Usage | Données | Accès | Différences avec la production |
|---|---|---|---|---|

## 7.2 Infrastructure de production

**Type** : `C4Deployment` · **Portée** : environnement de production

{bloc mermaid — pattern 7 de mermaid-patterns.md}

## 7.3 Nœuds

| Nœud | Stéréotype | Contient | Ressources | Zone réseau |
|---|---|---|---|---|

## 7.4 Protocoles et flux réseau

| Source | Destination | Protocole | Port | Chiffré | Authentifié |
|---|---|---|---|---|---|

## 7.5 Déploiement et rollback

| | |
|---|---|
| **Artefact déployé** | |
| **Procédure** | |
| **Interruption de service** | |
| **Rollback** | |
| **Migration de données réversible ?** | |

### Traçabilité
| Élément | Preuve | Hypothèse | Question ouverte | Risque |
|---|---|---|---|---|
```

---

## `08-concepts-transverses.md`

```markdown
# 8. Concepts transverses

> **Version** : 1.0.0  
> **LastUpdate** : AAAA-MM-JJ  
> **But** : Documenter les mécanismes qui traversent tous les blocs et qu'aucune section structurelle ne porte seule.

Chaque concept suit le même format :

> **Décision** · **Implémentation** (chemins réels) · **Limite connue** · **ADR**

Un concept non applicable est marqué `Non applicable` **avec justification** — il n'est pas
supprimé, sinon le lecteur ne sait pas s'il a été oublié ou écarté.

## 8.1 Identité et accès
## 8.2 Sécurité
## 8.3 Données
## 8.4 Interfaces et versionnement
## 8.5 Erreurs
## 8.6 Résilience
## 8.7 Configuration
## 8.8 Observabilité
## 8.9 Persistance
## 8.10 Messaging
## 8.11 Performance
## 8.12 Concurrence
## 8.13 Tests
## 8.14 Déploiement et rollback

### Traçabilité
| Élément | Preuve | Hypothèse | Question ouverte | Risque |
|---|---|---|---|---|
```

---

## `09-decisions.md`

```markdown
# 9. Décisions d'architecture

> **Version** : 1.0.0  
> **LastUpdate** : AAAA-MM-JJ  
> **But** : Indexer les décisions d'architecture tracées et leurs relations de remplacement.

Index seul, et seul index : le contenu d'un ADR vit dans `../adr/`, jamais recopié ici (une copie
divergerait), et ce dossier ne contient pas d'autre index.

| ID | Titre | Domaine | Statut | Date | Remplace | Remplacé par |
|---|---|---|---|---|---|---|
| [ARCH-001](../adr/ARCH-001-….md) | | architecture | Accepté | AAAA-MM-JJ | — | — |

## Statuts

`Proposé` · `Accepté` · `Rejeté` · `Remplacé` · `Déprécié`

## Décisions à tracer

Décisions structurantes identifiées mais non encore rédigées :

| Sujet | Pourquoi un ADR est nécessaire | Qui décide |
|---|---|---|

### Traçabilité
| Élément | Preuve | Hypothèse | Question ouverte | Risque |
|---|---|---|---|---|
```

---

## `10-exigences-qualite.md`

```markdown
# 10. Exigences qualité

> **Version** : 1.0.0  
> **LastUpdate** : AAAA-MM-JJ  
> **But** : Rendre les objectifs qualité mesurables au travers de scénarios vérifiables.

## 10.1 Tableau des qualités

| Qualité | Priorité | Sous-caractéristique | Objectif §1.4 |
|---|---|---|---|

## 10.2 Scénarios qualité

Détail dans [`quality/scenarios.md`](../quality/scenarios.md). Chaque scénario porte les
**sept attributs** obligatoires :

| Attribut | Contenu attendu |
|---|---|
| Stimulus | L'événement déclencheur |
| Environnement | État du système au moment du stimulus |
| Réponse | Comportement attendu |
| Mesure | La grandeur observée |
| Seuil | La valeur à ne pas dépasser / à atteindre |
| Méthode de vérification | Comment on le prouve |
| Propriétaire | Qui répond de ce scénario |

| ID | Type | Qualité | Résumé | Seuil | Vérification |
|---|---|---|---|---|---|
| QS-01 | Usage | | | | |
| QS-02 | Changement | | | | |
| QS-03 | Défaillance | | | | |

> Les trois types — **usage**, **changement**, **défaillance** — sont obligatoires. Ne couvrir que
> l'usage revient à ne tester que le beau temps.

### Traçabilité
| Élément | Preuve | Hypothèse | Question ouverte | Risque |
|---|---|---|---|---|
```

### `quality/scenarios.md`

```markdown
# Scénarios qualité

> **Version** : 1.0.0  
> **LastUpdate** : AAAA-MM-JJ  
> **But** : Détailler chaque scénario qualité avec ses sept attributs et son propriétaire.

## QS-01 — {titre}

| Attribut | Valeur |
|---|---|
| **Type** | Usage / Changement / Défaillance |
| **Qualité** | |
| **Stimulus** | |
| **Environnement** | |
| **Réponse attendue** | |
| **Mesure** | |
| **Seuil** | |
| **Méthode de vérification** | |
| **Propriétaire** | |
| **État** | Vérifié / Non vérifié / À définir |
| **Liens** | §{section}, {ID d'ADR} |
```

---

## `11-risques-dette.md`

```markdown
# 11. Risques et dette technique

> **Version** : 1.0.0  
> **LastUpdate** : AAAA-MM-JJ  
> **But** : Recenser et prioriser les risques d'architecture et la dette technique assumée.

Registre détaillé : [`risks/register.md`](../risks/register.md).

## 11.1 Risques

| ID | Risque | Probabilité | Impact | Exposition | Mitigation | Propriétaire | Date cible |
|---|---|---|---|---|---|---|---|
| R-01 | | Faible/Moyenne/Élevée | Faible/Moyen/Élevé | | | | |

## 11.2 Dette technique

| ID | Dette | Origine | Coût de portage | Coût de remboursement | Propriétaire | Date cible |
|---|---|---|---|---|---|---|
| D-01 | | | | | | |

> **Exposition** = probabilité × impact. Elle sert au tri, pas à la décoration.
> Un risque sans propriétaire n'est pas géré ; le noter reste utile, mais il faut le dire.

### Traçabilité
| Élément | Preuve | Hypothèse | Question ouverte | Risque |
|---|---|---|---|---|
```

---

## `12-glossaire.md`

```markdown
# 12. Glossaire

> **Version** : 1.0.0  
> **LastUpdate** : AAAA-MM-JJ  
> **But** : Fixer le vocabulaire métier et technique employé dans toute la documentation d'architecture.

## Termes métier

| Terme | Définition | Ne pas confondre avec |
|---|---|---|

## Termes techniques

| Terme | Définition | Où il apparaît |
|---|---|---|

## Acronymes

| Acronyme | Développé | Signification dans ce système |
|---|---|---|

> Un terme défini ici doit être **employé tel quel** dans les autres sections. Un synonyme
> introduit ailleurs crée deux concepts là où il n'y en a qu'un.
```
