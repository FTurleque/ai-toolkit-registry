# mcp-search-net

Donne à Claude une recherche Web et une lecture de pages qui passent par **votre** poste : un
serveur MCP local, en lecture seule, adossé à SearXNG et Crawl4AI, avec un catalogue
documentaire local en plus. Le serveur lui-même vit dans son dépôt
([FTurleque/mcp-search-net](https://github.com/FTurleque/mcp-search-net)) ; cet artefact contient ce
qu'il faut pour le brancher, et la règle qui dit à Claude quand s'en servir.

## Les outils apportés

| Outil | Ce qu'il fait |
|-------|---------------|
| `mcp__mcp-search-net__search_web` | découvre des pages via SearXNG, en privilégiant les domaines du registre officiel |
| `mcp__mcp-search-net__fetch_url` | lit une URL publique connue, protection SSRF, extraction Markdown, sections limitées |
| `mcp__mcp-search-net__search_docs` | cherche dans le catalogue documentaire local (`catalog.db`) |
| `mcp__mcp-search-net__read_doc_section` | lit une section d'un document du catalogue |
| `mcp__mcp-search-net__list_docs` | liste les documents du catalogue |
| `mcp__mcp-search-net__list_search_history` | historique des recherches — **opt-in**, absent des profils de production |

## Ce que ça change

Sans la règle `rules/mcp-search-net.md`, Claude n'utilise ces outils que si on les lui nomme. Avec
elle, il cherche de lui-même quand une information peut avoir changé (version, prix, API, loi), et
s'en abstient quand le dépôt ou le contexte suffisent.

## Prérequis

- mcp-search-net installé par son setup Windows (il fournit `bin\mcp-search-net.cmd`, la
  configuration et le catalogue) ;
- Docker Desktop, pour SearXNG et Crawl4AI ;
- la variable d'environnement `MCP_SEARCH_HOME` pointant vers le dossier d'installation.

## Ce que le serveur lit et écrit

- **Lit** : les pages publiques demandées (via Crawl4AI), les résultats SearXNG, son catalogue local.
- **Écrit** : son cache (`cache.sqlite`) et, seulement si activé, l'historique (`history.sqlite`),
  dans son dossier de données. Rien dans vos dépôts.
- **Envoie à l'extérieur** : les requêtes de recherche (via SearXNG, vers les moteurs configurés) et
  les requêtes HTTP vers les URL lues. Aucun LLM ni API commerciale.
- Ne parle que le protocole MCP sur `stdout` : aucun port applicatif n'est ouvert.

## Installation

Le setup de mcp-search-net peut configurer lui-même Claude Code et Claude Desktop ; cet extrait
sert à le faire à la main, ou à réparer une configuration.

1. **Claude Code** (portée utilisateur, tous les projets) :

   ```bash
   claude mcp add-json --scope user mcp-search-net '<objet "mcp-search-net" de .mcp.json>'
   ```

   Claude Code développe `${MCP_SEARCH_HOME}` au lancement du serveur. Pour un seul projet, fusionner
   `.mcp.json` dans `<projet>/.mcp.json`.
2. **Claude Desktop** : ajouter l'entrée dans `claude_desktop_config.json` en écrivant les chemins
   **résolus** — Desktop ne développe pas les variables.
3. **La règle** : copier `rules/mcp-search-net.md` dans `~/.claude/rules/` (tous les projets) ou
   `<projet>/.claude/rules/` (un projet).
4. Vérifier dans une nouvelle session que les outils `mcp__mcp-search-net__*` apparaissent.

## Limites

- Lancement vérifié sous Windows seulement (`cmd.exe` + script `.cmd`) ; le profil Docker du
  serveur n'est pas couvert par cet extrait.
- Sans Docker démarré, `search_web` et `fetch_url` échouent ; le catalogue local reste lisible.
- La qualité des résultats dépend des moteurs que SearXNG interroge et de leurs quotas.
- La règle est une consigne, pas un contrôle : Claude peut chercher trop ou trop peu.

## Vérifié

Branché en portée utilisateur dans Claude Code et dans Claude Desktop sur le poste du mainteneur,
outils visibles et appelés dans les deux. La même règle était recopiée dans le `CLAUDE.md` global :
la livrer ici évite les trois copies divergentes.
