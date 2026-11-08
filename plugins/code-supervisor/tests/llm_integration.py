"""Integration de la couche modele (llm.py) avec le vrai CLI `claude`. Opt-in : SUPERVISOR_LLM_IT=1.

Desactivee par defaut et en CI : deux cas appellent le modele, donc consomment du quota et dependent du reseau
et de la session de la personne qui lance les tests. Cout borne : modele `haiku`, un appel par cas, diffs de
quelques lignes.

- `revue_bug` : un diff introduit un bug evident ; la revue doit rendre au moins un constat qui le vise.
- `revue_propre` : un diff correct ; la revue ne doit rendre aucun CRITICAL.
- `non_authentifie`, `delai_depasse`, `sortie_non_json` : le hook de bout en bout avec un vrai CLI qui echoue
  (dossier de configuration vide, delai d'une seconde, `claude --version` a la place de la revue). Le verdict
  doit dire « analyse statique seule » et le hook ne jamais bloquer. Aucun de ces cas n'obtient de reponse du
  modele."""
from __future__ import annotations

import json
import os
import shutil
import sys
import time
from typing import List

from hook_scenarios import CLEAN, Sandbox

ENABLE_VAR = "SUPERVISOR_LLM_IT"
MODEL = "haiku"
REVIEW_TIMEOUT_SECONDS = 180
STATIC_ONLY = "analyse statique seule"
# Variables qui authentifient le CLI sans passer par le dossier de configuration.
AUTH_VARS = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "CLAUDE_CODE_OAUTH_TOKEN")

BASE = '''def average(values):
    """Moyenne arithmetique d'une liste non vide."""
    return sum(values) / len(values)


def last_items(items, count):
    """Les `count` derniers elements de `items`."""
    return items[-count:]
'''
BUGGED = BASE.replace("return sum(values) / len(values)", "return sum(values) / (len(values) + 1)")
FIXED = BASE.replace('''    """Moyenne arithmetique d'une liste non vide."""
    return sum(values) / len(values)''', '''    """Moyenne arithmetique ; zero pour une liste vide."""
    if not values:
        return 0.0
    return sum(values) / len(values)''')
BUG_LINE = 3                                   # le `return` qui fausse la division
BUG_WORDS = ("+ 1", "+1", "denominat", "dénominat")    # ce que seul un constat sur ce defaut mentionne


def enabled() -> bool:
    return os.environ.get(ENABLE_VAR) == "1"


def _engine(script: str):
    engine_dir = os.path.join(os.path.dirname(os.path.abspath(script)), "supervisor")
    sys.path.insert(0, engine_dir)
    try:
        import llm
        import source
        from config import DEFAULTS, Config
    finally:
        sys.path.remove(engine_dir)
    settings = json.loads(json.dumps(DEFAULTS))
    settings["llm"].update(enabled=True, cli="claude", model=MODEL, timeout_seconds=REVIEW_TIMEOUT_SECONDS)
    return llm, source, Config(settings)


def _review(sandbox: Sandbox, script: str, name: str, after: str):
    """Revue par modele d'un diff de `stats.py` : (constats du modele, verdict)."""
    llm, source, cfg = _engine(script)
    repo = sandbox.make_repo(name, {"stats.py": BASE})
    sandbox.git(repo, "add", ".")
    sandbox.git(repo, "commit", "-qm", "base")
    Sandbox.write(repo, "stats.py", after)
    files = source.load(repo, ["stats.py"], source.git_changed_lines(repo, ["stats.py"]))
    previous = os.environ.pop("SUPERVISOR_NO_LLM", None)
    outputs = []
    run_reviewer = llm._run_reviewer

    def recording(*args):
        output, error = run_reviewer(*args)
        outputs.append(output)
        return output, error

    llm._run_reviewer = recording         # relevé du coût annoncé par le CLI, sans second appel
    try:
        findings, verdict = llm.review(repo, files, [], cfg)
    finally:
        llm._run_reviewer = run_reviewer
        if previous is not None:
            os.environ["SUPERVISOR_NO_LLM"] = previous
    print("  %s : %s" % (name, _cost(outputs)))
    return findings, verdict


def _cost(outputs) -> str:
    """Cout et volume annonces par l'enveloppe de `claude -p --output-format json`."""
    try:
        envelope = json.loads(outputs[0] or "")
    except (IndexError, ValueError):
        return "cout non communique"
    usage = envelope.get("usage") or {}
    tokens = sum(int(usage.get(key) or 0) for key in
                 ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
    return "%.4f USD, %d jetons en entree, %s en sortie, %.0f s" % (
        float(envelope.get("total_cost_usd") or 0), tokens, usage.get("output_tokens", "?"),
        float(envelope.get("duration_ms") or 0) / 1000)


def _describe(findings) -> str:
    return "; ".join("%s %s:%s %s" % (f.severity, f.file, f.line, f.message[:80]) for f in findings) or "aucun constat"


def _targets_bug(finding) -> bool:
    if not finding.file.endswith("stats.py"):
        return False
    text = (finding.message + " " + finding.evidence).lower()
    return finding.line == BUG_LINE or any(word in text for word in BUG_WORDS)


def _review_problems(sandbox: Sandbox, script: str) -> List[str]:
    problems = []
    findings, verdict = _review(sandbox, script, "revue_bug", BUGGED)
    print("  revue_bug : %s" % _describe(findings))
    if verdict.startswith("revue LLM"):
        problems.append("revue_bug : revue indisponible (%s)" % verdict)
    elif not any(_targets_bug(f) for f in findings):
        problems.append("revue_bug : aucun constat sur la division faussee (%s)" % _describe(findings))
    findings, verdict = _review(sandbox, script, "revue_propre", FIXED)
    print("  revue_propre : %s" % _describe(findings))
    if verdict.startswith("revue LLM"):
        problems.append("revue_propre : revue indisponible (%s)" % verdict)
    critical = [f for f in findings if f.severity == "CRITICAL"]
    if critical:
        problems.append("revue_propre : CRITICAL sur un diff correct (%s)" % _describe(critical))
    return problems


def _version_reviewer(sandbox: Sandbox, claude: str) -> str:
    """CLI de revue qui repond par `claude --version` : une sortie du vrai CLI, mais pas du JSON."""
    script = os.path.join(sandbox.work, "version_claude.py")
    Sandbox.write(sandbox.work, "version_claude.py",
                  "import subprocess, sys\nsys.stdin.read()\n"
                  "proc = subprocess.run([%r, '--version'], stdout=subprocess.PIPE)\n"
                  "sys.stdout.write(proc.stdout.decode('utf-8', 'replace'))\nsys.exit(proc.returncode)\n" % claude)
    launcher = os.path.join(sandbox.work, "version_claude.cmd" if os.name == "nt" else "version_claude")
    Sandbox.write(sandbox.work, os.path.basename(launcher),
                  ("@echo off\r\n\"%s\" \"%s\"\r\n" if os.name == "nt" else "#!/bin/sh\nexec \"%s\" \"%s\"\n")
                  % (sys.executable, script))
    os.chmod(launcher, 0o755)
    return launcher


def _hook(sandbox: Sandbox, name: str, env: dict, user_llm=None, project_llm=None) -> dict:
    repo = sandbox.make_repo(name, {"b.py": CLEAN})
    user_config = os.path.join(sandbox.config_dir, "supervisor.config.json")
    if user_llm:
        Sandbox.write(sandbox.config_dir, "supervisor.config.json", json.dumps({"llm": user_llm}))
    if project_llm:
        os.makedirs(os.path.join(repo, ".claude"))
        Sandbox.write(repo, os.path.join(".claude", "supervisor.config.json"), json.dumps({"llm": project_llm}))
    sandbox.env, previous = env, sandbox.env
    try:
        return sandbox.run(repo, {"cwd": repo, "session_id": name})
    finally:
        sandbox.env = previous
        if os.path.exists(user_config):
            os.remove(user_config)


def _hook_problem(name: str, result: dict, expected: str) -> List[str]:
    stdout = result["stdout"]
    message = stdout.get("systemMessage", "") if isinstance(stdout, dict) else str(stdout)
    print("  %s : %s" % (name, message[:200]))
    problems = []
    if result["rc"] != 0 or (isinstance(stdout, dict) and stdout.get("decision") == "block"):
        problems.append("%s : le hook bloque ou echoue (code %s)" % (name, result["rc"]))
    if STATIC_ONLY not in message:
        problems.append("%s : le verdict ne dit pas « %s » : %s" % (name, STATIC_ONLY, message[:200]))
    if expected not in message:
        problems.append("%s : %r absent du verdict" % (name, expected))
    return problems


def _error_problems(sandbox: Sandbox, claude: str) -> List[str]:
    with_llm = {k: v for k, v in sandbox.env.items() if k != "SUPERVISOR_NO_LLM"}
    unauthenticated = {k: v for k, v in with_llm.items() if k not in AUTH_VARS}
    authenticated = {k: v for k, v in with_llm.items() if k != "CLAUDE_CONFIG_DIR"}
    if os.environ.get("CLAUDE_CONFIG_DIR"):
        authenticated["CLAUDE_CONFIG_DIR"] = os.environ["CLAUDE_CONFIG_DIR"]
    problems = []
    result = _hook(sandbox, "non_authentifie", unauthenticated,
                   user_llm={"enabled": True, "model": MODEL, "timeout_seconds": 60})
    problems += _hook_problem("non_authentifie", result, "revue LLM")
    result = _hook(sandbox, "delai_depasse", authenticated,
                   project_llm={"enabled": True, "model": MODEL, "timeout_seconds": 1})
    problems += _hook_problem("delai_depasse", result, "revue LLM indisponible (delai de 1 s depasse)")
    result = _hook(sandbox, "sortie_non_json", with_llm,
                   user_llm={"enabled": True, "cli": _version_reviewer(sandbox, claude), "timeout_seconds": 60})
    problems += _hook_problem("sortie_non_json", result, "revue LLM sans resultat exploitable")
    return problems


def problems(script: str) -> List[str]:
    claude = shutil.which("claude")
    if not claude:
        return ["CLI `claude` introuvable dans le PATH"]
    sandbox = Sandbox(script)
    started = time.time()
    try:
        found = _error_problems(sandbox, claude) + _review_problems(sandbox, script)
    finally:
        sandbox.close()
    print("  duree totale : %.0f s" % (time.time() - started))
    return found
