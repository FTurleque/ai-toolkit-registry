"""Justesse des CRITICAL : le moteur relit `precision/`, du code propre et realiste, et ne doit y rendre aucun CRITICAL.

Les autres suites figent le comportement, defauts compris ; celle-ci affirme un resultat attendu. Chaque fichier y
reprend des motifs legitimes qu'une regle a deja pris pour des defauts bloquants (requete parametree assemblee de
litteraux, liste `IN (?, ?)`, message d'erreur qui contient un mot SQL, boucle qui lit une liste remplie avant elle,
catch d'une ligne qui relance, chaine de connexion factice d'un test). Tous les fichiers sont lus comme nouveaux :
chaque ligne compte. Les constats MAJOR et MINOR ne sont pas evalues."""
from __future__ import annotations

import json
import os
import sys
from typing import List

CRITICAL = "CRITICAL"


def _walk(folder: str) -> List[str]:
    rels = []
    for current, dirs, files in os.walk(folder):
        dirs.sort()
        for name in sorted(files):
            rels.append(os.path.relpath(os.path.join(current, name), folder).replace("\\", "/"))
    return rels


def problems(engine_dir: str, precision_dir: str) -> List[str]:
    sys.path.insert(0, engine_dir)
    try:
        import engine
        import source
        from config import DEFAULTS, Config
    finally:
        sys.path.remove(engine_dir)
    settings = json.loads(json.dumps(DEFAULTS))
    settings["external_tools"] = []
    rels = _walk(precision_dir)
    files = source.load(precision_dir, rels, new_files=set(rels))
    if len(files) != len(rels):
        return ["%d fichier(s) de precision/ non lus par le moteur" % (len(rels) - len(files))]
    findings = engine.analyze(precision_dir, files, Config(settings))
    return ["%s:%s %s : %s" %(f.file, f.line, f.rule, f.message) for f in findings if f.severity == CRITICAL]


def count_files(precision_dir: str) -> int:
    return len(_walk(precision_dir))
