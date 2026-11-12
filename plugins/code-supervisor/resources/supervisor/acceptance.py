"""Constats acceptes : un projet ecarte un constat precis en ecrivant pourquoi il est faux.

La cle `accepted_findings` d'une configuration de projet est une liste d'entrees
`{"rule", "path", "symbol" (facultatif), "reason"}`. Une entree n'ecarte que les constats de sa regle, dans
les fichiers que `path` designe (chemin exact ou motif, comme `exclude`) et, si `symbol` est donne, pour ce
symbole seulement. Sans raison, elle n'ecarte rien. Une entree dont un fichier a ete relu sans qu'elle
ecarte quoi que ce soit est perimee : elle devient elle-meme un constat, pour que la liste ne pourrisse pas.
Une entree dont aucun fichier n'a ete relu n'est pas jugee : le superviseur ne relit que ce qui change."""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from typing import List, Optional, Tuple

from model import CAT_CONVENTION, MINOR, Finding

STALE_RULE = "SUP.STALE_ACCEPTANCE"


@dataclass(frozen=True)
class Acceptance:
    rule: str
    path: str
    symbol: Optional[str]
    reason: str

    def covers_path(self, rel_path: str) -> bool:
        path = rel_path.replace("\\", "/")
        return path == self.path or fnmatch.fnmatch(path, self.path)

    def covers(self, finding: Finding) -> bool:
        return (finding.rule == self.rule and self.covers_path(finding.file)
                and (self.symbol is None or finding.symbol == self.symbol))

    def label(self) -> str:
        return "%s sur %s%s" % (self.rule, self.path, " (`%s`)" % self.symbol if self.symbol else "")


def _text(entry: dict, key: str) -> str:
    value = entry.get(key)
    return value.strip() if isinstance(value, str) else ""


def parse(raw) -> Tuple[List[Acceptance], List[str]]:
    """Les entrees valides de `accepted_findings`, et une phrase par entree refusee."""
    if raw is None:
        return [], []
    if not isinstance(raw, list):
        return [], ["accepted_findings doit etre une liste : ignore"]
    entries, problems = [], []
    for index, entry in enumerate(raw):
        if not isinstance(entry, dict):
            problems.append("accepted_findings[%d] n'est pas un objet : ignore" % index)
            continue
        missing = [key for key in ("rule", "path", "reason") if not _text(entry, key)]
        symbol = entry.get("symbol")
        if symbol is not None and not (isinstance(symbol, str) and symbol.strip()):
            missing.append("symbol")
        if missing:
            problems.append("accepted_findings[%d] n'a pas de %s non vide : ignore, une acceptation dit ce "
                            "qu'elle ecarte et pourquoi" % (index, ", ".join(missing)))
            continue
        entries.append(Acceptance(_text(entry, "rule"), _text(entry, "path").replace("\\", "/"),
                                  symbol.strip() if symbol else None, _text(entry, "reason")))
    return entries, problems


def split(findings: List[Finding], entries: List[Acceptance]):
    """Les constats qu'aucune entree n'ecarte, puis les paires (constat, entree) ecartees."""
    kept, accepted = [], []
    for finding in findings:
        entry = next((candidate for candidate in entries if candidate.covers(finding)), None)
        if entry is None:
            kept.append(finding)
        else:
            accepted.append((finding, entry))
    return kept, accepted


def stale(entries: List[Acceptance], accepted, analysed_paths: List[str]) -> List[Finding]:
    """Un constat par entree dont un fichier a ete relu sans qu'elle ecarte rien."""
    used = {entry for _, entry in accepted}
    findings = []
    for entry in entries:
        relus = [path for path in analysed_paths if entry.covers_path(path)]
        if entry in used or not relus:
            continue
        findings.append(Finding(
            rule=STALE_RULE, category=CAT_CONVENTION, severity=MINOR,
            message="Acceptation perimee : %s n'ecarte plus aucun constat." % entry.label(),
            fix="Retirer cette entree de accepted_findings, ou corriger son symbole si le code a ete renomme.",
            file=relus[0], symbol=entry.symbol,
        ))
    return findings
