# Index du registre

Catalogue de tous les artefacts du depot, par type.

> Fichier genere par `python tools/generate_index.py`. Ne pas l'editer a la main.

## Resume

| Type | Nombre |
|------|-------:|
| Skills | 14 |
| Plugins | 1 |
| Sous-agents | 0 |
| Commandes | 0 |
| Hooks | 1 |
| Instructions de projet | 1 |
| Serveurs MCP | 4 |
| Styles de sortie | 0 |
| **Total** | **21** |

## Skills

| Artefact | Description | Version | Statut | Surfaces |
|----------|-------------|---------|--------|----------|
| [`adr-audit`](skills/architecture/adr-audit) | Audite l'ensemble des ADR (Architecture Decision Records) d'un projet et leur cohérence avec le dossier arc42, les changements OpenSpec et le code : inventai... | 1.0.1 | experimental | Code |
| [`adr-author`](skills/architecture/adr-author) | Décide si un ADR (Architecture Decision Record) est justifié, puis crée ou améliore le bon document, à partir d'un besoin, d'un changement OpenSpec ou d'une ... | 1.0.0 | experimental | Code |
| [`adr-check`](skills/architecture/adr-check) | Contrôle le respect des ADR (Architecture Decision Records) dans le code et la cohérence documentaire. Deux modes : contrôle d'un changement (diff, branche, ... | 1.0.0 | experimental | Code |
| [`adr-policy`](skills/architecture/adr-policy) | Ressources partagées par les skills adr-audit, adr-author et adr-check : politique de pertinence des ADR, découverte du contexte d'un projet, articulation av... | 1.1.0 | experimental | Code |
| [`arc42-architecture`](skills/architecture/arc42-architecture) | Audite la conformité d'une application au standard arc42, puis crée, complète ou corrige sa documentation d'architecture dans docs/architecture/ : les 12 sec... | 3.0.0 | experimental | Code |
| [`audit-application`](skills/development/audit-application) | Audit de code complet d'une application (architecture, qualité, sécurité, tests, performance, dépendances, CI/CD) produisant un rapport versionné dans le dép... | 1.1.0 | experimental | Code, Desktop |
| [`code-to-openspec`](skills/development/code-to-openspec) | Rétro-ingénierie d'une application existante à partir de son code, puis préparation de changements OpenSpec traçables (constats, exigences, scénarios, tâches... | 1.0.0 | experimental | Code, Desktop |
| [`generate-uml-diagrams`](skills/architecture/generate-uml-diagrams) | Génère un jeu de diagrammes UML pertinent, en Mermaid, pour un module, un sous-module ou l'application (vue d'ensemble globale dans docs/diagrams/application... | 1.0.1 | experimental | Code |
| [`generate-windows-exe`](skills/development/generate-windows-exe) | Empaquette une application en executable Windows (.exe) via Inno Setup ou jpackage, avec un driver reproductible. | 1.1.0 | stable | Code, Desktop |
| [`git-submodule-common`](skills/development/git-submodule-common) | Module Python partagé par les skills publish-git-submodule et install-git-submodule : exécution de git sans shell, validation des chemins, branches et URL, a... | 1.0.0 | experimental | Code |
| [`install-git-submodule`](skills/development/install-git-submodule) | Installe dans le dépôt courant un sous-module Git qui suit une branche d'un autre dépôt (le dépôt entier, ou la branche d'export d'un dossier publiée par pub... | 1.0.0 | experimental | Code |
| [`java-code-review`](skills/development/java-code-review) | Analyse du code Java afin d'identifier les défauts, risques et améliorations possibles. | 1.1.0 | stable | Code, Desktop, claude.ai, API |
| [`publish-git-submodule`](skills/development/publish-git-submodule) | Prépare un dépôt entier, ou un seul de ses dossiers (.claude, docs, une bibliothèque), pour être installé comme sous-module Git dans d'autres dépôts, puis au... | 1.0.1 | experimental | Code |
| [`setup-app-documentation`](skills/architecture/setup-app-documentation) | Met en place, organise et complète toute la documentation d'une application dans docs/ : arborescence par lecteur (user/, developer/, architecture/, project/... | 1.0.0 | experimental | Code |

## Plugins

| Artefact | Description | Version | Statut | Surfaces |
|----------|-------------|---------|--------|----------|
| [`code-supervisor`](plugins/code-supervisor) | Supervision automatique du code produit par un agent, avec renvoi en correction sur probleme bloquant. | 1.4.0 | experimental | Code |

## Hooks

| Artefact | Description | Version | Statut | Surfaces |
|----------|-------------|---------|--------|----------|
| [`rtk`](hooks/rtk) | Hook PreToolUse sur Bash qui fait passer les commandes de Claude Code par RTK (Rust Token Killer) pour condenser leur sortie avant qu'elle n'entre dans le co... | 1.0.0 | experimental | Code |

## Instructions de projet

| Artefact | Description | Version | Statut | Surfaces |
|----------|-------------|---------|--------|----------|
| [`user-global-rules`](instructions/user-global-rules) | Règles à poser dans ~/.claude/rules/ pour qu'elles s'appliquent à tous les projets : langue des réponses, et interdiction de créer fichiers, dossiers ou work... | 1.0.0 | experimental | Code |

## Serveurs MCP

| Artefact | Description | Version | Statut | Surfaces |
|----------|-------------|---------|--------|----------|
| [`jetbrains-ide`](mcp/jetbrains-ide) | Branche le serveur MCP intégré aux IDE JetBrains (IntelliJ IDEA 2025.2 et plus) : inspections, recherche dans le projet ouvert, refactorisations, configurati... | 1.0.0 | brouillon | Code |
| [`mcp-search-net`](mcp/mcp-search-net) | Branche le serveur local mcp-search-net : recherche Web (SearXNG), lecture de pages publiques protégée contre le SSRF et catalogue documentaire local, en lec... | 1.0.0 | experimental | Code, Desktop |
| [`minos`](mcp/minos) | Branche le serveur MCP de MINOS, moteur local d'intelligence de code : symboles, appelants, implémentations, dépendances, architecture, impact d'un changemen... | 1.0.0 | experimental | Code, Desktop |
| [`nexus`](mcp/nexus) | Branche le serveur MCP de NEXUS, moteur local de contexte : recherche hybride dans le code et la documentation, recherche de symboles et d'usages, et constru... | 1.0.0 | experimental | Code, Desktop |
