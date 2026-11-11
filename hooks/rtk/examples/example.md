# Exemple — entrée et sortie réelles du hook

Relevé avec RTK 0.49.0 sous Windows.

**Entrée** reçue par le hook sur l'entrée standard (extrait) :

```json
{"tool_name":"Bash","tool_input":{"command":"git status"}}
```

**Sortie** du hook (`rtk hook claude`) :

```json
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecisionReason":"RTK auto-rewrite","updatedInput":{"command":"rtk git status"}}}
```

Claude Code exécute donc `rtk git status`, et Claude reçoit la sortie condensée.

**Contrôle à blanc**, sans lancer la commande :

```bash
rtk hook check "git status"
# rtk git status
```
