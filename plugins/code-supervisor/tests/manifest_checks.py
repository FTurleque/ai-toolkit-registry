"""Coherence de hooks/hooks.json avec le README et l'installeur.

Pas de reference figee : chaque controle est une assertion. Une divergence entre la forme declaree du hook,
la commande documentee et le timeout de l'installation manuelle fait echouer la suite."""
from __future__ import annotations

import json
import os
import re
from typing import List

EVENTS = ("Stop", "SubagentStop")
SHELL_COMMAND = 'python "${CLAUDE_PLUGIN_ROOT}/resources/supervisor.py"'
FORM_SENTENCE = "Le hook est declare en forme %s"


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _install_timeout(plugin_dir: str):
    match = re.search(r"^HOOK_TIMEOUT_SECONDS\s*=\s*(\d+)\s*$",
                      _read(os.path.join(plugin_dir, "resources", "install.py")), re.M)
    return int(match.group(1)) if match else None


def _handlers(groups) -> list:
    if not isinstance(groups, list):
        return []
    return [h for g in groups if isinstance(g, dict) for h in (g.get("hooks") or []) if isinstance(h, dict)]


def _handler_problems(event: str, handlers: list, timeout) -> List[str]:
    if len(handlers) != 1:
        return ["%s : un seul handler attendu, %d trouve(s)" % (event, len(handlers))]
    handler = handlers[0]
    problems = []
    if handler.get("type") != "command":
        problems.append("%s : type %r, 'command' attendu" % (event, handler.get("type")))
    if "args" not in handler and handler.get("command") != SHELL_COMMAND:
        problems.append("%s : commande %r, %r attendue" % (event, handler.get("command"), SHELL_COMMAND))
    if handler.get("timeout") != timeout:
        problems.append("%s : timeout %r, HOOK_TIMEOUT_SECONDS de install.py vaut %r"
                        % (event, handler.get("timeout"), timeout))
    return problems


def _readme_problems(readme: str, forms: set) -> List[str]:
    announced = {form for form in ("exec", "shell") if FORM_SENTENCE % form in readme}
    problems = ["README.md n'annonce pas la forme %s utilisee par hooks/hooks.json" % form
                for form in sorted(forms - announced)]
    problems += ["README.md annonce la forme %s, absente de hooks/hooks.json" % form
                 for form in sorted(announced - forms)]
    if "shell" in forms and SHELL_COMMAND not in readme:
        problems.append("README.md ne reprend pas la commande du hook : %s" % SHELL_COMMAND)
    return problems


def problems(plugin_dir: str) -> List[str]:
    try:
        manifest = json.loads(_read(os.path.join(plugin_dir, "hooks", "hooks.json")))
    except (OSError, ValueError) as exc:
        return ["hooks/hooks.json illisible : %s" % exc]
    hooks = manifest.get("hooks") if isinstance(manifest, dict) else None
    if not isinstance(hooks, dict) or sorted(hooks) != sorted(EVENTS):
        return ["hooks/hooks.json doit declarer exactement les evenements %s" % ", ".join(EVENTS)]
    timeout = _install_timeout(plugin_dir)
    found: List[str] = []
    forms = set()
    for event in EVENTS:
        handlers = _handlers(hooks[event])
        found.extend(_handler_problems(event, handlers, timeout))
        forms.update("exec" if "args" in h else "shell" for h in handlers)
    readme = " ".join(_read(os.path.join(plugin_dir, "README.md")).split())
    found.extend(_readme_problems(readme, forms))
    return found
