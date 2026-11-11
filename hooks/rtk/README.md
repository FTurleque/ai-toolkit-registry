# RTK — sorties de commandes condensées

Un hook `PreToolUse` qui intercepte chaque commande Bash de Claude Code et la fait passer par
[RTK](https://github.com/rtk-ai/rtk) (Rust Token Killer) : `git status` devient `rtk git status`, et
Claude reçoit une sortie condensée au lieu de la sortie brute. RTK est un outil tiers ; cet
artefact contient seulement son branchement et la règle qui l'accompagne.

## Ce que ça change

- Les commandes bavardes (git, build, tests, docker, gh) coûtent nettement moins de jetons ; RTK
  annonce 60 à 90 % selon les commandes, mesurable avec `rtk gain`.
- La règle `rules/rtk.md` dit à Claude de prendre la sortie condensée pour complète et de ne
  repasser en brut (`rtk proxy <cmd>`) que si elle est inutilisable.

## Événement, effet, risques

| | |
|---|---|
| Événement | `PreToolUse`, outil `Bash` uniquement |
| Effet | réécrit la commande avant exécution ; ne bloque rien |
| Ce qu'il écrit | rien dans le dépôt ; RTK tient ses statistiques et ses sorties complètes en cas d'échec dans son propre dossier de données |
| Risque | une sortie trop condensée peut cacher un détail ; d'où la règle et `rtk proxy` |

Les outils intégrés `Read`, `Grep` et `Glob` ne passent pas par Bash : le hook ne les touche pas.

## Installation

Voie conseillée, celle de l'éditeur : installer `rtk`, puis `rtk init -g`, qui pose le hook et le
fichier d'instructions dans `~/.claude/`. Vérifier avec `rtk init --show`.

Voie manuelle, depuis ce dépôt :

1. Installer `rtk` et vérifier `rtk gain` (un autre projet porte le même nom : `rtk gain` doit
   exister).
2. Fusionner `settings.hooks.json` dans `~/.claude/settings.json`, sans écraser les hooks présents.
3. Copier `rules/rtk.md` dans `~/.claude/rules/`.
4. Relancer Claude Code ; `rtk hook check "git status"` montre la réécriture prévue.

Retrait : `rtk init -g --uninstall`, ou retirer le handler du `settings.json` et la règle.

## Limites

- Claude Code uniquement : les hooks n'existent pas ailleurs.
- Ne s'applique qu'aux commandes que RTK sait traiter ; les autres passent inchangées.
- `timeout` fixé à 10 s dans l'extrait (l'installation de l'éditeur n'en met pas) : le hook rend
  la main en quelques millisecondes.
- Vérifié sous Windows avec RTK 0.49.0, hook en place dans `~/.claude/settings.json` du mainteneur.
