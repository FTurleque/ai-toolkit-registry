#!/usr/bin/env python3
"""Controle statique des fichiers de diagrammes produits par le skill generate-uml-diagrams.

Verifie la forme attendue d'un fichier `docs/diagrams/<module>/<type>-<sujet>.md` (nom, titre, un
seul bloc mermaid, sections Lecture et Sources) et repere les pieges de syntaxe Mermaid les plus
courants. Ce controle ne fait aucun rendu : un resultat vert ne prouve pas que le diagramme
s'affiche, il ecarte seulement les erreurs reconnaissables.

Usage :
  python check_mermaid.py <fichier.md | dossier> [...]
  python check_mermaid.py --self-test

Code de sortie : 0 sans erreur (les avertissements n'echouent pas), 1 si au moins une erreur.
Prerequis : Python 3.8 ou plus, bibliotheque standard seulement.
"""
from __future__ import annotations

import os
import re
import sys
import tempfile

FLOWCHART_TYPES = ("component", "deployment", "package", "usecase", "activity", "communication",
                   "interaction")
TYPES = {"class": "classDiagram", "object": "classDiagram", "sequence": "sequenceDiagram",
         "state": "stateDiagram-v2", "er": "erDiagram"}
TYPES.update(dict.fromkeys(FLOWCHART_TYPES, "flowchart"))

FILE_NAME = re.compile(r"^(?P<type>[a-z]+)-(?P<subject>[a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})\s*(\S*)")
HEADER = re.compile(r"^(classDiagram|sequenceDiagram|stateDiagram-v2|stateDiagram|erDiagram"
                    r"|flowchart|graph)\b(.*)$")
FLOW_DIRECTION = re.compile(r"^\s*(TB|TD|BT|RL|LR)\s*$")
FLOW_ARROW = r"(?:-->|---|-\.->|==>|-\.-)"
SEQ_OPENERS = re.compile(r"^(alt|opt|loop|par|critical|break|rect|box)\b")
SEQ_ARROW = r"-->>|->>|--x|-x|--\)|-\)|-->|->"
SEQ_MESSAGE = re.compile(r"^[^:%%]+?(%s)[^:]*:" % SEQ_ARROW)
CLASS_RELATION = re.compile(
    r"^([A-Za-z_]\w*)\s*(?:\"[^\"]*\"\s*)?"
    r"(?:<\|--|\*--|o--|-->|--|\.\.>|\.\.\|>|\.\.|<--|--\*|--o|--\|>)"
    r"\s*(?:\"[^\"]*\"\s*)?([A-Za-z_]\w*)")
ER_ENTITY_OPEN = re.compile(r"^([A-Za-z_][\w-]*)\s*\{\s*$")
ER_RELATION = re.compile(r"^([A-Za-z_][\w-]*)\s+[|}o{.\-]+\s+([A-Za-z_][\w-]*)")
# Forme du noeud entre crochets : cylindre [( )], sous-programme [[ ]], parallelogramme [/ /].
SHAPED_LABEL = re.compile(r"^[(\[/\\]")
FORBIDDEN = [
    (re.compile(r"%%\{"), "directive %%{...}%% : ignoree ou bloquee par GitHub et GitLab"),
    (re.compile(r"^\s*style\s"), "instruction style : depend du moteur de rendu"),
    (re.compile(r"^\s*classDef\s"), "instruction classDef : depend du moteur de rendu"),
    (re.compile(r"^\s*click\s"), "instruction click : bloquee par GitHub et GitLab"),
]
LIMITS = {
    "classDiagram": ("classes", 10),
    "sequenceDiagram": ("participants", 8),
    "stateDiagram-v2": ("etats", 12),
    "erDiagram": ("entites", 10),
    "flowchart": ("noeuds", 15),
}
SEQ_MESSAGES_LIMIT = 25
LABEL_MAX_CHARS = 60

Lines = list  # liste de (numero de ligne, texte)


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, where: str, message: str) -> None:
        self.errors.append("%s : %s" % (where, message))

    def warn(self, where: str, message: str) -> None:
        self.warnings.append("%s : %s" % (where, message))


# --------------------------------------------------------------------------- extraction des blocs

def closes_fence(match: re.Match, fence: str) -> bool:
    marker = match.group(1)
    return marker[0] == fence[0] and len(marker) >= len(fence) and not match.group(2)


def mermaid_blocks(lines: list[str]) -> list[tuple[int, list[str]]]:
    """Blocs ```mermaid du fichier, avec le numero de ligne de leur premiere ligne."""
    blocks: list[tuple[int, list[str]]] = []
    fence = None
    current: list[str] | None = None
    for number, line in enumerate(lines, 1):
        match = FENCE.match(line)
        if fence is None and match:
            fence = match.group(1)
            if match.group(2).lower() == "mermaid":
                current = []
                blocks.append((number + 1, current))
        elif fence is not None and match and closes_fence(match, fence):
            fence, current = None, None
        elif current is not None:
            current.append(line)
    return blocks


def strip_comment(line: str) -> str:
    """Vide les commentaires %% ; garde les directives %%{ pour qu'elles soient signalees."""
    stripped = line.strip()
    if stripped.startswith("%%") and not stripped.startswith("%%{"):
        return ""
    return line.rstrip()


# --------------------------------------------------------------------------- structure du fichier

def check_file_name(name: str, report: Report) -> str | None:
    match = FILE_NAME.match(name)
    if not match:
        report.error(name, "nom attendu <type>-<sujet>.md, en kebab-case ASCII")
        return None
    if match.group("type") not in TYPES:
        report.error(name, "type inconnu %r ; types admis : %s"
                     % (match.group("type"), ", ".join(sorted(TYPES))))
        return None
    return match.group("type")


def check_structure(path: str, lines: list[str], report: Report) -> str | None:
    """Nom, titre, bandeau, sections. Rend le type annonce par le nom de fichier, ou None."""
    name = os.path.basename(path)
    expected_type = check_file_name(name, report)
    text = "\n".join(lines)
    if not lines or not lines[0].startswith("# "):
        report.error(name, "la premiere ligne doit etre un titre de niveau 1")
    if not re.search(r"^(> )?\*\*Module\*\*", text, re.M):
        report.warn(name, "bandeau '> **Module** : ... **Question** : ...' absent")
    elif "**Question**" not in text:
        report.warn(name, "le bandeau ne dit pas a quelle question repond le diagramme")
    for section in ("## Lecture", "## Sources"):
        if not re.search(r"^%s\s*$" % re.escape(section), text, re.M):
            report.error(name, "section '%s' absente" % section)
    return expected_type


# --------------------------------------------------------------------------- diagramme

def parse_header(where: str, header_line: str, expected_type: str | None,
                 report: Report) -> str | None:
    """Famille de diagramme declaree en premiere ligne, normalisee ; None si inconnue."""
    header = HEADER.match(header_line.strip())
    if not header:
        report.error(where, "type de diagramme absent ou inconnu en premiere ligne : %r"
                     % header_line.strip())
        return None
    kind = header.group(1)
    if kind == "graph":
        report.warn(where, "'graph' est l'ancien nom : ecrire 'flowchart'")
        kind = "flowchart"
    elif kind == "stateDiagram":
        report.error(where, "ecrire 'stateDiagram-v2'")
        kind = "stateDiagram-v2"
    if kind == "flowchart" and not FLOW_DIRECTION.match(header.group(2) or ""):
        report.warn(where, "flowchart sans direction (TD, LR...)")
    if expected_type and TYPES[expected_type] != kind:
        report.error(where, "le prefixe '%s' attend un %s, le bloc est un %s"
                     % (expected_type, TYPES[expected_type], kind))
    return kind


def check_common_lines(name: str, lines: Lines, report: Report) -> None:
    for number, line in lines:
        here = "%s:%d" % (name, number)
        for pattern, message in FORBIDDEN:
            if pattern.search(line):
                report.error(here, message)
        for label in re.findall(r'"([^"]*)"', line):
            if len(label) > LABEL_MAX_CHARS:
                report.warn(here, "libelle de %d caracteres, a raccourcir" % len(label))


def check_diagram(name: str, start: int, block: list[str], expected_type: str | None,
                  report: Report) -> None:
    body = [strip_comment(line) for line in block]
    content = [(start + index, line) for index, line in enumerate(body) if line.strip()]
    if not content:
        report.error(name, "bloc mermaid vide")
        return
    first_number, first = content[0]
    kind = parse_header("%s:%d" % (name, first_number), first, expected_type, report)
    if kind is None:
        return
    lines = content[1:]
    check_common_lines(name, lines, report)
    CHECKERS[kind](name, first_number, lines, report)


def limit_warning(name: str, first: int, kind: str, count: int, report: Report) -> None:
    label, limit = LIMITS[kind]
    if count > limit:
        report.warn("%s:%d" % (name, first), "%d %s (repere : %d) : envisager de scinder"
                    % (count, label, limit))


# --------------------------------------------------------------------------- flowchart

def flow_nodes_of(line: str) -> set[str]:
    """Identifiants de noeuds d'une ligne : un en tete de chaque segment entre deux fleches."""
    if re.match(r"^\s*(subgraph|end|direction)\b", line):
        return set()
    bare = re.sub(r'"[^"]*"|\|[^|]*\|', "", line)
    bare = re.sub(r"-\.\s[^.]*\s\.->", "-->", bare)  # libelle de fleche pointillee : -. txt .->
    segments = re.split(r"[ox<]?(?:--+|-\.+-|==+)[->ox]?", bare)
    nodes = set()
    for segment in segments:
        nodes.update(re.findall(r"(?:^|&)\s*([A-Za-z_]\w*)", segment.strip()))
    return nodes


def count_flow_nodes(lines: Lines) -> int:
    nodes: set[str] = set()
    for _, line in lines:
        nodes |= flow_nodes_of(line)
    return len(nodes)


def unquoted_special_labels(line: str) -> list[str]:
    """Libelles [..] et {..} non proteges qui contiennent un caractere special."""
    found = [label for label in re.findall(r"\w\[([^\]\"][^\]]*)\]", line)
             if not SHAPED_LABEL.match(label) and re.search(r"[(){}<>#]", label)]
    found += [label for label in re.findall(r"\w\{([^}\"{][^}]*)\}", line)
              if re.search(r"[()\[\]<>#]", label)]
    return found


def flow_line_errors(line: str) -> list[str]:
    errors = []
    if re.search(r"(^|[\s>|&])end\s*[\[\(\{]|%s\s*(\|[^|]*\|\s*)?end\s*$" % FLOW_ARROW, line):
        errors.append("noeud nomme 'end' en minuscules : il ferme le bloc en cours")
    if re.search(r"(?:--+|-\.+-|==+)[ox]\w", line):
        errors.append("'---o' ou '---x' colle a un identifiant : ajouter un espace")
    errors += ["libelle avec caracteres speciaux non mis entre guillemets : %r" % label
               for label in unquoted_special_labels(line)]
    return errors


def check_subgraphs(name: str, first: int, lines: Lines, report: Report) -> None:
    depth = 0
    previous = ""
    for number, line in lines:
        stripped = line.strip()
        if re.match(r"^subgraph\b", stripped):
            depth += 1
        elif stripped == "end":
            here = "%s:%d" % (name, number)
            if re.match(r"^subgraph\b", previous):
                report.error(here, "subgraph vide : le rendu echoue, y mettre au moins un noeud")
            if depth == 0:
                report.error(here, "'end' sans 'subgraph' ouvert")
            depth = max(depth - 1, 0)
        previous = stripped
    if depth > 0:
        report.error("%s:%d" % (name, first), "%d 'subgraph' non ferme(s) par 'end'" % depth)


def check_flowchart(name: str, first: int, lines: Lines, report: Report) -> None:
    check_subgraphs(name, first, lines, report)
    for number, line in lines:
        stripped = line.strip()
        if stripped in ("end",) or stripped.startswith("subgraph"):
            continue
        for message in flow_line_errors(stripped):
            report.error("%s:%d" % (name, number), message)
    limit_warning(name, first, "flowchart", count_flow_nodes(lines), report)


# --------------------------------------------------------------------------- sequence

class SequenceState:
    def __init__(self) -> None:
        self.depth = 0
        self.active: dict[str, int] = {}
        self.participants: set[str] = set()
        self.messages = 0


def sequence_message(where: str, line: str, state: SequenceState, report: Report) -> None:
    state.messages += 1
    head, text = line.split(":", 1)
    for end in re.split(SEQ_ARROW, head):
        end = end.strip().lstrip("+-")
        if end:
            state.participants.add(end)
    if ";" in text:
        report.error(where, "';' dans un message termine l'instruction : ecrire #59;")


def sequence_line(where: str, line: str, state: SequenceState, report: Report) -> None:
    declared = re.match(r"^(participant|actor)\s+(\S+)", line)
    toggle = re.match(r"^(activate|deactivate)\s+(\S+)", line)
    if declared:
        state.participants.add(declared.group(2))
    elif SEQ_OPENERS.match(line):
        state.depth += 1
    elif line == "end":
        if state.depth == 0:
            report.error(where, "'end' sans bloc alt/opt/loop/par ouvert")
        state.depth = max(state.depth - 1, 0)
    elif toggle:
        step = 1 if toggle.group(1) == "activate" else -1
        state.active[toggle.group(2)] = state.active.get(toggle.group(2), 0) + step
    elif SEQ_MESSAGE.match(line):
        sequence_message(where, line, state, report)


def check_sequence(name: str, first: int, lines: Lines, report: Report) -> None:
    state = SequenceState()
    for number, line in lines:
        sequence_line("%s:%d" % (name, number), line.strip(), state, report)
    where = "%s:%d" % (name, first)
    if state.depth > 0:
        report.error(where, "%d bloc(s) alt/opt/loop/par non ferme(s)" % state.depth)
    for participant in (p for p, balance in state.active.items() if balance != 0):
        report.error(where, "activate/deactivate desequilibres pour %s" % participant)
    limit_warning(name, first, "sequenceDiagram", len(state.participants), report)
    if state.messages > SEQ_MESSAGES_LIMIT:
        report.warn(where, "%d messages (repere : %d) : scinder par scenario"
                    % (state.messages, SEQ_MESSAGES_LIMIT))


# --------------------------------------------------------------------------- class, state, er

def check_braces(name: str, first: int, lines: Lines, report: Report) -> None:
    depth = 0
    for number, line in lines:
        depth += line.count("{") - line.count("}")
        if depth < 0:
            report.error("%s:%d" % (name, number), "'}' sans '{' ouvrante")
            depth = 0
    if depth > 0:
        report.error("%s:%d" % (name, first), "%d accolade(s) non fermee(s)" % depth)


def class_names_of(line: str) -> set[str]:
    declared = re.match(r"^class\s+([A-Za-z_]\w*)", line)
    if declared:
        return {declared.group(1)}
    relation = CLASS_RELATION.match(line)
    return set(relation.groups()) if relation else set()


def check_class(name: str, first: int, lines: Lines, report: Report) -> None:
    check_braces(name, first, lines, report)
    classes: set[str] = set()
    for number, line in lines:
        stripped = line.strip()
        classes |= class_names_of(stripped)
        if "<<" not in stripped and re.search(r"[A-Za-z_]<[A-Za-z_][\w, ]*>", stripped):
            report.error("%s:%d" % (name, number), "generique en <T> : ecrire ~T~")
    limit_warning(name, first, "classDiagram", len(classes), report)


def check_state(name: str, first: int, lines: Lines, report: Report) -> None:
    check_braces(name, first, lines, report)
    states: set[str] = set()
    for number, line in lines:
        stripped = line.strip()
        states.update(re.findall(r"([A-Za-z_]\w*)\s*(?=-->)", stripped))
        states.update(re.findall(r"-->\s*([A-Za-z_]\w*)", stripped))
        if re.search(r"-->\s*end\b|^end\s*-->|^state\s+end\b", stripped):
            report.error("%s:%d" % (name, number), "etat nomme 'end' en minuscules")
    limit_warning(name, first, "stateDiagram-v2", len(states), report)


def check_er(name: str, first: int, lines: Lines, report: Report) -> None:
    """Les accolades des cardinalites (||--o{) ne comptent pas : seuls les blocs d'entite."""
    entities: set[str] = set()
    open_at = None
    for number, line in lines:
        stripped = line.strip()
        here = "%s:%d" % (name, number)
        entity = ER_ENTITY_OPEN.match(stripped)
        relation = ER_RELATION.match(stripped)
        if entity:
            if open_at is not None:
                report.error(here, "bloc d'entite ouvert avant la fermeture du precedent")
            entities.add(entity.group(1))
            open_at = number
        elif stripped == "}":
            if open_at is None:
                report.error(here, "'}' sans bloc d'entite ouvert")
            open_at = None
        elif relation and open_at is None:
            entities.update(relation.groups())
        elif open_at is not None and re.match(r"^\w+\(", stripped):
            report.warn(here, "type d'attribut avec parentheses : refuse par certaines versions")
    if open_at is not None:
        report.error("%s:%d" % (name, open_at), "bloc d'entite non ferme")
    limit_warning(name, first, "erDiagram", len(entities), report)


CHECKERS = {
    "flowchart": check_flowchart,
    "sequenceDiagram": check_sequence,
    "classDiagram": check_class,
    "stateDiagram-v2": check_state,
    "erDiagram": check_er,
}


# --------------------------------------------------------------------------- execution

def check_file(path: str, report: Report) -> None:
    with open(path, encoding="utf-8") as handle:
        lines = handle.read().splitlines()
    name = os.path.basename(path)
    expected_type = check_structure(path, lines, report)
    blocks = mermaid_blocks(lines)
    if not blocks:
        report.error(name, "aucun bloc ```mermaid")
        return
    if len(blocks) > 1:
        report.error(name, "%d blocs mermaid : un fichier = un diagramme" % len(blocks))
    for start, block in blocks:
        check_diagram(name, start, block, expected_type, report)


def markdown_files(directory: str) -> list[str]:
    found = []
    for root, _, names in os.walk(directory):
        found += [os.path.join(root, n) for n in sorted(names)
                  if n.endswith(".md") and n.lower() != "readme.md"]
    return found


def collect(paths: list[str]) -> list[str]:
    files: list[str] = []
    for path in paths:
        if not os.path.exists(path):
            raise SystemExit("introuvable : %s" % path)
        files += markdown_files(path) if os.path.isdir(path) else [path]
    return files


def run(paths: list[str]) -> int:
    """Sortie standard = resultat de l'outil, comme pour tools/validate.py."""
    files = collect(paths)
    report = Report()
    for path in files:
        check_file(path, report)
    for line in report.errors:
        print("ERREUR  " + line)
    for line in report.warnings:
        print("AVERT.  " + line)
    print("%d fichier(s), %d erreur(s), %d avertissement(s)"
          % (len(files), len(report.errors), len(report.warnings)))
    return 1 if report.errors else 0


# --------------------------------------------------------------------------- auto-test

def framed(title: str, diagram: str) -> str:
    return ("# %s\n\n> **Module** : `billing` · **Type** : test · **Question** : test ?\n\n"
            "```mermaid\n%s\n```\n\n## Lecture\n\n- test\n\n## Sources\n\n- `X.java`\n"
            % (title, diagram.strip("\n")))


GOOD = {
    "sequence-paiement.md": """sequenceDiagram
    participant A as Api
    participant S as Service
    A->>S: payer(id)
    alt accepte
        S-->>A: ok
    else refuse
        S-->>A: erreur
    end""",
    "er-facturation.md": """erDiagram
    CLIENT ||--o{ FACTURE : "recoit"
    FACTURE }|--|{ LIGNE : "contient"
    FACTURE {
        uuid id PK
        varchar statut
    }""",
    "state-facture.md": """stateDiagram-v2
    [*] --> Brouillon
    Brouillon --> Emise : emettre
    note right of Emise
        envoyee au client
    end note
    Emise --> [*]""",
    "component-contexte.md": """flowchart LR
    API["API"] --> DB[("Base PostgreSQL")]
    API --> SUB[["Sous-programme"]]
    %% commentaire ordinaire
    API --> PSP["Prestataire"]""",
}

BAD = """# Composants

```mermaid
flowchart
    %%{init: {"theme": "dark"}}%%
    A[payer(montant)] --> end[Fin]
    subgraph vide
    end
    subgraph x
    A---oB
```

```mermaid
classDiagram
    class A
```
"""

BAD_ER = """erDiagram
    FACTURE {
        uuid id PK
    CLIENT ||--o{ FACTURE : "recoit"
"""

EXPECTED_ERRORS = ["nom attendu", "section '## Lecture'", "blocs mermaid", "caracteres speciaux",
                   "nomme 'end'", "'---o'", "non ferme", "attend un classDiagram",
                   "subgraph vide", "directive", "bloc d'entite non ferme"]


def check_texts(cases: dict[str, str]) -> Report:
    """Ecrit chaque texte sous son nom dans un dossier temporaire et le controle."""
    report = Report()
    with tempfile.TemporaryDirectory() as tmp:
        for name, text in cases.items():
            path = os.path.join(tmp, name)
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(text)
            check_file(path, report)
    return report


def self_test() -> int:
    ok = check_texts({name: framed(name, diagram) for name, diagram in GOOD.items()})
    ko = check_texts({"class-composants.md": BAD, "er-casse.md": framed("er", BAD_ER),
                      "Sequence Paiement.md": framed("x", GOOD["sequence-paiement.md"])})
    nodes = count_flow_nodes([(1, 'A --> B["service (v2)"] --> C'), (2, "C -. lien .-> D & E")])
    failures = []
    if nodes != 5:
        failures.append("comptage des noeuds : %d au lieu de 5" % nodes)
    if ok.errors:
        failures.append("des fichiers corrects produisent des erreurs : %s" % ok.errors)
    missing = [e for e in EXPECTED_ERRORS if not any(e in line for line in ko.errors)]
    if missing:
        failures.append("erreurs attendues non detectees : %s" % missing)
    for failure in failures:
        print("ECHEC  " + failure)
    print("auto-test : %s" % ("OK" if not failures else "ECHEC"))
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    if argv == ["--self-test"]:
        return self_test()
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if argv else 2
    return run(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
