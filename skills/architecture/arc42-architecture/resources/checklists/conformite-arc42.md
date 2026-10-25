# Grille d'audit de conformité arc42

Grille appliquée en **Phase 1 — AUDIT** du skill `arc42-architecture`.

Chaque critère reçoit un verdict, **accompagné d'une preuve** (chemin de fichier) ou d'un constat
d'absence. Un critère sans preuve citée n'est pas audité, il est supposé — et une supposition n'a
pas sa place dans un rapport d'audit.

## Verdicts

| Verdict | Signification | Gravité |
|---|---|---|
| ✅ Conforme | Présent, structuré arc42, cohérent avec le dépôt | — |
| 🟡 Partiel | Présent mais incomplet | Moyenne |
| ⚠️ Divergent | Présent et **contredit par le dépôt** | **Maximale** |
| ❌ Absent | Aucune trace | Haute |
| ➖ Non applicable | Justification obligatoire | — |

> ⚠️ **Divergent passe avant Absent dans le rapport.** Un lecteur qui suit une documentation fausse
> prend de mauvaises décisions ; un lecteur face à une documentation absente sait qu'il doit
> chercher.

---

## 0 — Outillage et structure

| # | Critère | Verdict |
|---|---|---|
| 0.1 | `docs/architecture/` existe | |
| 0.2 | Les 12 fichiers `arc42/NN-*.md` existent et sont non vides | |
| 0.3 | Aucune section arc42 dupliquée ailleurs dans le dépôt (deux sources de vérité) | |
| 0.4 | `adr/` existe et ne contient que des ADR au format Archgate (`<PRÉFIXE>-<NNN>-<slug>.md` avec front matter `id`, `title`, `domain`, `rules`), et leurs `.rules.ts` | |
| 0.5 | Les diagrammes sont en Mermaid — aucun ASCII, aucune image binaire comme source, aucun C4 reproduit à la main en `flowchart` | |
| 0.6 | Les niveaux `C4Context` et `C4Container` sont présents | |
| 0.7 | Entête `Version / LastUpdate / But` sur chaque fichier | |
| 0.8 | La documentation est référencée depuis le `README.md` racine et le `CLAUDE.md` | |
| 0.9 | Aucun secret ni donnée personnelle dans la documentation ou les diagrammes | |
| 0.10 | Si Archgate est utilisé : `.archgate/config.json` déclare `paths.adrs: "docs/architecture/adr"`, `.archgate/lint/` existe, aucun ADR ne reste dans `.archgate/adrs/` | |

---

## 1 — Introduction et objectifs

| # | Critère | Verdict |
|---|---|---|
| 1.1 | Résumé du système compréhensible sans connaissance préalable | |
| 1.2 | Objectifs métier explicites | |
| 1.3 | Parties prenantes nommées avec leur attente | |
| 1.4 | **3 à 5 objectifs qualité priorisés** (pas une liste plate de 12 adjectifs) | |
| 1.5 | Chaque objectif qualité est mesurable ou renvoie à un scénario en section 10 | |

## 2 — Contraintes

| # | Critère | Verdict |
|---|---|---|
| 2.1 | Contraintes métier | |
| 2.2 | Contraintes techniques (versions imposées, socle, compatibilité) | |
| 2.3 | Contraintes réglementaires (RGPD, CRA, hébergement, archivage légal) | |
| 2.4 | Contraintes organisationnelles (équipes, calendrier, processus) | |
| 2.5 | **Distinction explicite contrainte imposée vs préférence d'équipe** | |
| 2.6 | Origine de chaque contrainte citée (qui l'impose) | |

## 3 — Contexte et périmètre

| # | Critère | Verdict |
|---|---|---|
| 3.1 | Frontière du système sans ambiguïté (ce qui est dedans, ce qui est dehors) | |
| 3.2 | Tous les acteurs humains listés | |
| 3.3 | Tous les systèmes externes listés | |
| 3.4 | Interfaces décrites (sens, données échangées, protocole) | |
| 3.5 | **Diagramme `C4Context`** en Mermaid | |
| 3.6 | Aucun système externe présent dans la config du dépôt et absent du diagramme | |

## 4 — Stratégie de solution

| # | Critère | Verdict |
|---|---|---|
| 4.1 | Principes architecturaux énoncés | |
| 4.2 | Style de décomposition nommé et **conforme à l'arborescence réelle des sources** | |
| 4.3 | Technologies structurantes identifiées | |
| 4.4 | Mécanisme explicite pour **chaque** objectif qualité de la section 1 | |
| 4.5 | Liens vers les ADR correspondants | |

## 5 — Vue des blocs de construction

| # | Critère | Verdict |
|---|---|---|
| 5.1 | **Diagramme `C4Container`** en Mermaid | |
| 5.2 | Diagrammes `C4Component` pour les conteneurs complexes uniquement | |
| 5.3 | `classDiagram` pour les zones critiques, si utile | |
| 5.4 | Pour chaque bloc : **responsabilité** | |
| 5.5 | Pour chaque bloc : **interfaces** exposées et consommées | |
| 5.6 | Pour chaque bloc : **dépendances** | |
| 5.7 | Pour chaque bloc : **chemin du code source** | |
| 5.8 | Aucun bloc documenté sans code correspondant, aucun module du dépôt absent | |
| 5.9 | Aucun mélange de niveaux C4 dans un même diagramme | |

## 6 — Vue d'exécution

| # | Critère | Verdict |
|---|---|---|
| 6.1 | **≥ 1 scénario métier nominal** | |
| 6.2 | **≥ 1 scénario d'erreur** | |
| 6.3 | **≥ 1 scénario d'exploitation** (démarrage, reprise, bascule, batch) | |
| 6.4 | Chaque scénario en `sequenceDiagram` Mermaid | |
| 6.5 | **Noms strictement identiques à la section 5** | |
| 6.6 | Comportement en cas d'échec explicite (timeout, retry, compensation, journalisation) | |

## 7 — Vue de déploiement

| # | Critère | Verdict |
|---|---|---|
| 7.1 | Environnements pertinents listés (dev, recette, préprod, prod) | |
| 7.2 | Nœuds, zones réseau, instances, conteneurs, stockages | |
| 7.3 | Protocoles et ports significatifs | |
| 7.4 | **Diagramme `C4Deployment`** en Mermaid, nœuds imbriqués zone → machine → runtime → conteneur | |
| 7.5 | Cohérence avec les Dockerfiles, manifestes k8s / Helm / IaC réellement présents | |
| 7.6 | Mécanisme de mise à jour et de rollback décrit | |

## 8 — Concepts transverses

Un concept non applicable est marqué ➖ **avec justification** ; il n'est pas omis.

| # | Concept | Verdict |
|---|---|---|
| 8.1 | Identité et accès (authentification, autorisation, rôles) | |
| 8.2 | Sécurité (surface d'attaque, chiffrement, secrets, durcissement) | |
| 8.3 | Données (modèle, cycle de vie, rétention, anonymisation) | |
| 8.4 | Interfaces et versionnement (compatibilité, dépréciation) | |
| 8.5 | Erreurs (taxonomie, propagation, messages utilisateur) | |
| 8.6 | Résilience (timeouts, retries, circuit breaker, dégradation) | |
| 8.7 | Configuration (sources, priorités, rechargement) | |
| 8.8 | Observabilité (logs, métriques, traces, alertes) | |
| 8.9 | Persistance (transactions, migrations, cohérence) | |
| 8.10 | Messaging (files, événements, idempotence, ordre) | |
| 8.11 | Performance (budgets, caches, pagination) | |
| 8.12 | Concurrence (verrous, sessions, accès concurrents) | |
| 8.13 | Tests (niveaux, couverture attendue, jeux de données) | |
| 8.14 | Déploiement et rollback | |

## 9 — Décisions

| # | Critère | Verdict |
|---|---|---|
| 9.1 | Index présent avec identifiant, titre, statut, date, relation de remplacement | |
| 9.2 | **Aucun ADR recopié en entier** dans la section | |
| 9.3 | Chaque ADR de `adr/` figure dans l'index, et réciproquement | |
| 9.4 | Aucun ADR `Accepté` supprimé de l'historique | |
| 9.5 | Chaque décision structurante visible dans le code possède un ADR | |
| 9.6 | Numérotation unique et séquentielle par préfixe ; l'`id` du front matter égal au début du nom de fichier | |

## 10 — Exigences qualité

| # | Critère | Verdict |
|---|---|---|
| 10.1 | Tableau des qualités (arbre ou liste priorisée) | |
| 10.2 | Scénarios d'**usage** | |
| 10.3 | Scénarios de **changement** | |
| 10.4 | Scénarios de **défaillance** | |
| 10.5 | Chaque scénario porte : **stimulus, environnement, réponse, mesure, seuil, méthode de vérification, propriétaire** | |
| 10.6 | Chaque objectif qualité de la section 1 possède au moins un scénario | |

## 11 — Risques et dette technique

| # | Critère | Verdict |
|---|---|---|
| 11.1 | Risques et dette priorisés | |
| 11.2 | Chaque entrée porte : **probabilité, impact, exposition, mitigation, propriétaire, date cible** | |
| 11.3 | Les contournements assumés dans le code sont présents dans le registre | |
| 11.4 | Aucun risque sans propriétaire | |

## 12 — Glossaire

| # | Critère | Verdict |
|---|---|---|
| 12.1 | Termes métier définis | |
| 12.2 | Termes techniques propres au système définis | |
| 12.3 | Acronymes ambigus levés | |
| 12.4 | Vocabulaire du glossaire réellement utilisé dans les autres sections | |

---

## Barème de synthèse

Le score sert à situer l'application, pas à la noter :

| Conformité | Lecture |
|---|---|
| 12/12 conformes, 0 divergent | Documentation d'architecture opérationnelle — reste à maintenir |
| ≥ 9 conformes, 0 divergent | Base saine, compléter les sections partielles |
| Toute divergence ⚠️ | **Corriger les divergences avant tout ajout de section** |
| ≤ 4 conformes | Intégration complète à mener, en une seule passe |
| Aucune trace de `docs/architecture/` | Amorçage — mode INTÉGRATION intégral |

**Règle de priorisation du plan de migration** :
1. Divergences ⚠️ (documentation fausse) ;
2. Sections 3, 5, 7 absentes (personne ne comprend le système) ;
3. ADR manquants sur décisions coûteuses à inverser ;
4. Section 10 sans scénarios mesurables ;
5. Le reste.
