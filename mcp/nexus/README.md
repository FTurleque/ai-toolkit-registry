# NEXUS Context Engine

Donne à Claude un moteur de **sélection de contexte** :
[NEXUS](https://github.com/FTurleque/nexus-context-engine) indexe le code, la documentation, les
instructions et les skills de vos projets, puis rend un contexte pertinent, borné par un budget et
dont chaque élément dit d'où il vient. Le moteur vit dans son dépôt ; cet artefact contient le
branchement MCP.

## Les outils apportés

| Outil | Ce qu'il fait |
|-------|---------------|
| `mcp__nexus__list_projects` | liste les projets indexés |
| `mcp__nexus__search_code` | recherche hybride dans un projet |
| `mcp__nexus__search_across_projects` | la même, sur plusieurs projets (100 au plus) |
| `mcp__nexus__find_symbol` | trouve un symbole |
| `mcp__nexus__find_usages` | trouve ses usages |
| `mcp__nexus__build_context` | construit un contexte sous budget pour une demande |
| `mcp__nexus__build_context_across_projects` | la même, fédérée |
| `mcp__nexus__explain_context` / `explain_context_across_projects` | explique pourquoi chaque élément a été retenu |

## Ce que ça change

Pour une question qui touche plusieurs fichiers ou plusieurs dépôts, Claude demande un contexte
déjà trié au lieu d'ouvrir des fichiers un par un, et peut justifier ce qu'il a lu.

## Prérequis

- Docker, et le conteneur `nexus-context-engine` démarré (runtime Docker de NEXUS) ;
- les projets à interroger indexés par NEXUS.

## Ce que le serveur lit et écrit

- **Lit** : les projets montés et indexés dans le conteneur, son index SQLite et Lucene.
- **Écrit** : ses index, dans son stockage (`NEXUS_HOME` du conteneur). Les outils MCP n'écrivent
  pas dans vos dépôts.
- **Envoie à l'extérieur** : rien ; la recherche sémantique, quand elle est activée, est locale.

## Installation

1. Démarrer le conteneur `nexus-context-engine`.
2. **Claude Code** : `claude mcp add-json --scope user nexus '<objet "nexus" de .mcp.json>'`.
3. **Claude Desktop** : ajouter l'entrée telle quelle dans `claude_desktop_config.json` (aucun
   chemin à résoudre).
4. Vérifier dans une nouvelle session que les outils `mcp__nexus__*` apparaissent, puis appeler
   `list_projects`.

## Limites

- Conteneur arrêté : `docker exec` échoue et le serveur n'apparaît pas dans la session.
- Le nom du conteneur est figé dans l'extrait (`nexus-context-engine`) : à adapter si vous le
  renommez.
- Ne répond que sur ce qui est indexé ; la fédération est limitée à 100 projets.
- Le budget de contexte est une borne : un contexte coupé peut manquer un élément utile,
  `explain_context` aide à le voir.

## Vérifié

Branché en portée utilisateur dans Claude Code et dans Claude Desktop sur le poste du mainteneur,
outils visibles et appelables dans les deux.
