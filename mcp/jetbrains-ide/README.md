# Serveur MCP des IDE JetBrains (IntelliJ IDEA)

Depuis la version 2025.2, IntelliJ IDEA et les autres IDE JetBrains embarquent un **serveur MCP**.
Branché sur Claude Code, il lui donne accès à ce que l'IDE sait du projet ouvert : ses
inspections, son index, ses refactorisations, ses configurations d'exécution. Rien à installer
d'autre que le plugin MCP Server, livré et activé avec l'IDE.

## Les outils apportés

Préfixés `mcp__jetbrains__`. La liste dépend de l'IDE et de sa version ; elle se règle dans
`Settings | Tools | MCP Server | Exposed Tools`, outil par outil. Familles typiques :

| Famille | Exemples |
|---------|----------|
| Analyse | `get_file_problems` (inspections de l'IDE sur un fichier) |
| Navigation et recherche | recherche de fichiers, de texte et de symboles dans le projet |
| Édition et refactorisation | lecture et modification de fichiers, renommage par l'IDE |
| Exécution | configurations d'exécution, `execute_terminal_command` |
| Autres | base de données, VCS, selon l'IDE |

## Ce que ça change

Claude obtient les erreurs et avertissements tels que l'IDE les voit (compilation, inspections),
et peut renommer un symbole par la refactorisation de l'IDE plutôt que par un chercher-remplacer.

## Prérequis

- IntelliJ IDEA (ou un autre IDE JetBrains) 2025.2 ou plus, **ouvert** sur le projet ;
- `Settings | Tools | MCP Server` → **Enable MCP Server** coché.

## Ce que le serveur lit et écrit

- **Lit** : tout le projet ouvert dans l'IDE, ses index et ses inspections.
- **Écrit** : les fichiers du projet (édition, refactorisation) et peut **lancer des commandes** et
  des configurations d'exécution. Par défaut, `execute_terminal_command` et l'exécution demandent
  une confirmation dans l'IDE ; le « brave mode » la supprime — à laisser désactivé.
- **Envoie à l'extérieur** : rien par lui-même ; il n'écoute que sur `127.0.0.1`.

## Installation

Voie conseillée : dans l'IDE, `Settings | Tools | MCP Server`, section de configuration des
clients, **Auto-Configure** pour Claude Code. L'IDE écrit lui-même l'entrée avec le bon port.

Voie manuelle (ou pour réparer) :

1. Dans l'IDE, `Copy HTTP Stream Config` (menu à côté d'Auto-Configure) et relever le port.
2. Définir `JETBRAINS_MCP_PORT`, puis
   `claude mcp add-json --scope user jetbrains '<objet "jetbrains" de .mcp.json>'` ;
   ou directement `claude mcp add --scope user --transport http jetbrains http://127.0.0.1:<port>/stream`.
3. Vérifier avec `claude mcp list` que `jetbrains` est connecté, l'IDE étant ouvert.

## Limites

- IDE fermé : le serveur est injoignable et Claude Code le signale au démarrage.
- Chaque instance d'IDE a son port ; avec plusieurs IDE ouverts, l'entrée ne vise que l'un d'eux.
- Le port peut changer d'une version de l'IDE à l'autre : refaire Auto-Configure après une mise à
  jour si la connexion échoue.
- Déclaré pour Claude Code seulement : Claude Desktop n'a pas été essayé.
- Les outils exposés varient selon l'IDE et sa version ; ne pas présumer d'un outil sans le voir.

## Vérifié

L'entrée existe en portée utilisateur dans Claude Code sur le poste du mainteneur (transport HTTP
stream, créée depuis IntelliJ IDEA). Au moment de l'ajout au registre, `claude mcp list` la
donnait injoignable (IDE fermé) : la connexion reste à revérifier IDE ouvert, d'où le statut
`draft`.
