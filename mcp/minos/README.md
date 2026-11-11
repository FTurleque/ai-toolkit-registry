# MINOS — Code Intelligence

Donne à Claude une connaissance structurée et persistante des dépôts indexés par
[MINOS](https://github.com/FTurleque/minos-code-intelligence) : au lieu de relire des fichiers au
hasard, il interroge un index de symboles, de relations et de dépendances. Le moteur vit dans son
dépôt ; cet artefact contient le branchement MCP.

## Les outils apportés

Tous préfixés `mcp__minos__`. Les principaux, par famille :

| Famille | Outils |
|---------|--------|
| Symboles et usages | `minos_find_symbols`, `minos_find_usages`, `minos_find_callers`, `minos_find_callees`, `minos_find_implementations`, `minos_symbol_context` |
| Structure | `minos_project_structure`, `minos_architecture`, `minos_architecture_graph`, `minos_module_context`, `minos_dependencies`, `minos_dependents`, `minos_program_graph` |
| Impact | `minos_impact`, `minos_impact_v2`, `minos_related_tests`, `minos_security_paths` |
| Recherche | `minos_search_code`, `minos_semantic_search`, `minos_hybrid_search`, `minos_hybrid_context` |
| Runtime et index | `minos_runtime_report`, `minos_runtime_sessions`, `minos_runtime_symbol`, `minos_index_status`, `minos_semantic_index_status` |
| Équipe | `minos_team_*` (espaces de travail, membres, audit) |

La liste exacte dépend de la version installée : `claude mcp get minos` ou la liste des outils de
la session fait foi.

## Ce que ça change

« Qui appelle cette méthode ? », « que casse ce changement ? », « quels tests couvrent ce module ? »
reçoivent une réponse tirée de l'index, avec sa provenance, au lieu d'une recherche textuelle
approximative. MINOS dit quand une capacité n'est pas disponible plutôt que de deviner.

## Prérequis

- MINOS installé par son setup Windows : `minos.exe` sous `<dossier du programme>\app\`, runtime
  Java embarqué, rien à cloner ;
- `MINOS_INSTALL_DIR` (dossier du programme) et `MINOS_HOME` (dossier de données) définis ;
- les dépôts à interroger indexés par MINOS ;
- en mode avancé, le backend MCP peut être `docker` : le routage reste derrière `minos.exe mcp`,
  l'extrait ne change pas.

## Ce que le serveur lit et écrit

- **Lit** : les dépôts que vous avez indexés (sources, historique Git) et ses propres index.
- **Écrit** : ses index et snapshots, dans `MINOS_HOME` (ou PostgreSQL/pgvector si configuré).
  Les outils MCP n'écrivent pas dans vos dépôts.
- **Envoie à l'extérieur** : rien par défaut. Le provider sémantique `ollama` appelle un Ollama
  local ; le stockage PostgreSQL parle à la base configurée.

## Installation

Le setup de MINOS peut configurer lui-même Claude Code et Claude Desktop ; cet extrait sert à le
faire à la main, ou à réparer une configuration.

1. **Claude Code** : `claude mcp add-json --scope user minos '<objet "minos" de .mcp.json>'`, ou
   fusion dans `<projet>/.mcp.json` pour un seul projet.
2. **Claude Desktop** : ajouter l'entrée dans `claude_desktop_config.json` avec les chemins résolus.
3. Vérifier dans une nouvelle session que les outils `mcp__minos__*` apparaissent, puis appeler
   `minos_index_status`.

## Limites

- Ne répond que sur ce qui est indexé : un dépôt non indexé ou un index en retard donne des
  réponses incomplètes, que `minos_index_status` permet de détecter.
- Lancement vérifié sous Windows (`minos.exe`) uniquement.
- La recherche sémantique est optionnelle (`disabled | local-hash | ollama`) : désactivée, les
  outils `semantic` et `hybrid` le signalent.

## Vérifié

Branché en portée utilisateur dans Claude Code et dans Claude Desktop sur le poste du mainteneur,
outils visibles et appelables dans les deux.
