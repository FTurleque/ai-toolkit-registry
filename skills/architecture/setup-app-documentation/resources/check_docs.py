#!/usr/bin/env python3
"""Controle l'organisation de docs/ d'une application.

Usage :
  python check_docs.py [--root DIR] [--json]
  python check_docs.py --self-test

Erreurs (code de sortie 1) :
  - fichier a la racine de docs/ autre que README.md ;
  - dossier de premier niveau hors user/, developer/, architecture/, project/ ;
  - lien Markdown relatif vers un fichier absent ;
  - fichier .md de docs/architecture/adr/ qui n'est pas une ADR (<PREFIXE>-<NNN>-<slug>.md) :
    Archgate lit chaque .md du dossier et signale les autres (unparsedAdrs) ;
  - ADR dont l'id du front matter differe du debut du nom de fichier ;
  - ADR restee dans .archgate/adrs/ alors que paths.adrs designe un autre dossier.
Avertissements (code 0) :
  - dossier de pages sans README.md, page ni liee ni nommee dans l'index de son dossier ;
  - sous-dossier dans le registre d'ADR (Archgate ne le lit pas) ;
  - page de docs/user/ qui cite un chemin src/, une commande de build ou un SHA.

Bibliotheque standard seulement (Python 3.8+). Lecture seule.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile

TOP_DIRS = {"user", "developer", "architecture", "project"}
ADR_DIR = ("architecture", "adr")
LOCAL_DIRS = {"rapport-supervisor"}
ADR_FILE = re.compile(r"^([A-Z][A-Z0-9]*-\d+)-[a-z0-9]+(?:-[a-z0-9]+)*\.(?:md|rules\.ts)$")
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FENCE = re.compile(r"^\s*(```|~~~)")
USER_SMELLS = [
    (re.compile(r"(?<![\w/])src/"), "chemin src/"),
    (re.compile(r"\./(?:mvnw|gradlew)\b|\bmvn\s+\w|\bnpm\s+run\b|\bgradle\s+\w"), "commande de build"),
    (re.compile(r"\b[0-9a-f]{40}\b"), "SHA de commit"),
]


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, where, message):
        self.errors.append({"where": where, "message": message})

    def warn(self, where, message):
        self.warnings.append({"where": where, "message": message})


def posix(path):
    return path.replace(os.sep, "/")


def read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def links_of(text):
    """Cibles des liens Markdown hors blocs de code."""
    targets, in_fence = [], False
    for line in text.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        line = re.sub(r"`[^`]*`", "", line)
        targets.extend(m.group(1) for m in LINK.finditer(line))
    return targets


def is_external(target):
    return bool(re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I)) or target.startswith("#")


def front_matter_id(text):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    match = re.search(r"^id:\s*['\"]?([^'\"\s]+)", text[3:end], re.M)
    return match.group(1) if match else None


def walk(docs):
    for current, dirs, files in os.walk(docs):
        rel = os.path.relpath(current, docs)
        parts = () if rel == "." else tuple(posix(rel).split("/"))
        dirs[:] = sorted(d for d in dirs if not (parts == ("project",) and d in LOCAL_DIRS))
        yield parts, dirs, sorted(files)


def check_structure(docs, rep):
    for name in sorted(os.listdir(docs)):
        path = os.path.join(docs, name)
        if os.path.isfile(path) and name != "README.md":
            rep.error("docs/" + name, "fichier a la racine de docs/ : seul README.md y a sa place")
        if os.path.isdir(path) and name not in TOP_DIRS:
            rep.error("docs/" + name + "/", "dossier de premier niveau non prevu (user, developer, architecture, project)")
    if not os.path.isfile(os.path.join(docs, "README.md")):
        rep.error("docs/README.md", "aiguillage absent")


def check_links(docs, rep):
    for parts, _dirs, files in walk(docs):
        folder = os.path.join(docs, *parts)
        for name in files:
            if not name.endswith(".md"):
                continue
            rel = "/".join(("docs",) + parts + (name,))
            for target in links_of(read(os.path.join(folder, name))):
                if is_external(target):
                    continue
                clean = target.split("#", 1)[0].split("?", 1)[0]
                if not clean:
                    continue
                if not os.path.exists(os.path.normpath(os.path.join(folder, clean))):
                    rep.error(rel, "lien casse : %s" % target)


def index_links(index_text):
    return {posix(os.path.normpath(t.split("#", 1)[0])) for t in links_of(index_text) if not is_external(t)}


def check_folder_index(folder, rel, pages, children, rep):
    index = os.path.join(folder, "README.md")
    if not os.path.isfile(index):
        rep.warn(rel, "pas de README.md d'index")
        return
    index_text = read(index)
    linked = index_links(index_text)
    for page in pages:
        if page not in linked and page not in index_text:
            rep.warn(rel + page, "page absente de l'index %sREADME.md" % rel)
    for child in children:
        if not any(link == child or link.startswith(child + "/") for link in linked):
            rep.warn(rel + child + "/", "sous-dossier absent de l'index %sREADME.md" % rel)


def check_indexes(docs, rep):
    """Index des dossiers de pages ; docs/architecture/ releve du skill arc42-architecture."""
    for parts, dirs, files in walk(docs):
        if not parts or parts[0] == "architecture":
            continue
        folder = os.path.join(docs, *parts)
        pages = [f for f in files if f.endswith(".md") and f != "README.md"]
        children = [d for d in dirs if os.listdir(os.path.join(folder, d))]
        if pages or children:
            check_folder_index(folder, "docs/" + "/".join(parts) + "/", pages, children, rep)


def check_adr_entry(adr, name, rep):
    rel = "docs/architecture/adr/" + name
    path = os.path.join(adr, name)
    if os.path.isdir(path):
        rep.warn(rel + "/", "sous-dossier dans le registre : Archgate ne le lit pas")
        return
    if not name.endswith(".md"):
        return  # Archgate ne lit que les .md : .gitkeep, .rules.ts, tsconfig.json des regles
    match = ADR_FILE.match(name)
    if not match:
        rep.error(rel, "pas une ADR (<PREFIXE>-<NNN>-<slug>.md) : Archgate la signalerait dans unparsedAdrs")
        return
    declared = front_matter_id(read(path))
    if declared != match.group(1):
        rep.error(rel, "id du front matter %r different du nom de fichier %r" % (declared, match.group(1)))


def declared_registry(root, rep):
    """Registre declare par .archgate/config.json, ou None sans configuration lisible."""
    config = os.path.join(root, ".archgate", "config.json")
    if not os.path.isfile(config):
        return None
    try:
        paths = json.loads(read(config)).get("paths") or {}
    except ValueError:
        rep.error(".archgate/config.json", "JSON illisible")
        return None
    return paths.get("adrs") or ".archgate/adrs"


def check_archgate_layout(root, registry, rep):
    if posix(registry).strip("/") == ".archgate/adrs":
        return
    legacy = os.path.join(root, ".archgate", "adrs")
    if os.path.isdir(legacy):
        for name in sorted(n for n in os.listdir(legacy) if n.endswith(".md")):
            rep.error(".archgate/adrs/" + name, "ADR hors du registre declare (%s)" % registry)
    elif not os.path.isdir(os.path.join(root, ".archgate", "lint")):
        rep.error(".archgate/", "ni lint/ ni adrs/ : Archgate ne reconnaitra pas le projet")


def check_adr_registry(root, docs, rep):
    adr = os.path.join(docs, *ADR_DIR)
    if os.path.isdir(adr):
        for name in sorted(os.listdir(adr)):
            check_adr_entry(adr, name, rep)
    registry = declared_registry(root, rep)
    if registry is not None:
        check_archgate_layout(root, registry, rep)


def check_user_pages(docs, rep):
    user = os.path.join(docs, "user")
    if not os.path.isdir(user):
        return
    for current, _dirs, files in os.walk(user):
        if "release-notes" in posix(os.path.relpath(current, user)).split("/"):
            continue
        for name in sorted(files):
            if not name.endswith(".md"):
                continue
            path = os.path.join(current, name)
            rel = "docs/" + posix(os.path.relpath(path, docs))
            text = read(path)
            for pattern, label in USER_SMELLS:
                if pattern.search(text):
                    rep.warn(rel, "page utilisateur qui cite un %s : contenu developer/ ou project/" % label)


def run(root):
    rep = Report()
    docs = os.path.join(root, "docs")
    if not os.path.isdir(docs):
        rep.error("docs/", "dossier absent")
        return rep
    check_structure(docs, rep)
    check_links(docs, rep)
    check_indexes(docs, rep)
    check_adr_registry(root, docs, rep)
    check_user_pages(docs, rep)
    return rep


def print_report(rep):
    for level, items in (("ERREUR", rep.errors), ("AVERTISSEMENT", rep.warnings)):
        for item in items:
            print("%s  %s : %s" % (level, item["where"], item["message"]))
    print("\n%d erreur(s), %d avertissement(s)." % (len(rep.errors), len(rep.warnings)))


# --------------------------------------------------------------------------- auto-test

def write(base, rel, text=""):
    path = os.path.join(base, *rel.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


class SelfTestFailure(Exception):
    pass


def expect(condition, detail):
    if not condition:
        raise SelfTestFailure(detail)


def self_test():
    base = tempfile.mkdtemp(prefix="check-docs-")
    try:
        write(base, "docs/README.md", "[user](user/README.md) [dev](developer/README.md)\n")
        write(base, "docs/user/README.md", "[Installer](INSTALL.md)\n")
        write(base, "docs/user/INSTALL.md", "Lancer `app`.\n")
        write(base, "docs/developer/README.md", "[Build](BUILD.md)\n")
        write(base, "docs/developer/BUILD.md", "```\n[pas un lien](absent.md)\n```\n./mvnw verify\n")
        write(base, "docs/architecture/adr/ARCH-001-hexagonal.md", "---\nid: ARCH-001\n---\n")
        write(base, "docs/architecture/adr/tsconfig.json", "{}")
        write(base, ".archgate/config.json", '{"paths": {"adrs": "docs/architecture/adr"}}')
        write(base, ".archgate/lint/.gitkeep")
        write(base, "docs/project/rapport-supervisor/rapport.md", "[casse](nulle-part.md)\n")
        clean = run(base)
        expect(not clean.errors and not clean.warnings, (clean.errors, clean.warnings))

        write(base, "docs/NOTES.md")
        write(base, "docs/adr/0001-x.md")
        write(base, "docs/user/INSTALL.md", "Voir [build](../developer/ABSENT.md), src/Main.java\n")
        write(base, "docs/user/FAQ.md")
        write(base, "docs/architecture/adr/README.md")
        write(base, "docs/architecture/adr/ARCH-002-db.md", "---\nid: ARCH-003\n---\n")
        write(base, ".archgate/adrs/GEN-001-example.md", "---\nid: GEN-001\n---\n")
        rep = run(base)
        errors = {(e["where"], e["message"].split(" :")[0].split(" (")[0]) for e in rep.errors}
        expected = {
            ("docs/NOTES.md", "fichier a la racine de docs/"),
            ("docs/adr/", "dossier de premier niveau non prevu"),
            ("docs/user/INSTALL.md", "lien casse"),
            ("docs/architecture/adr/README.md", "pas une ADR"),
            ("docs/architecture/adr/ARCH-002-db.md", "id du front matter 'ARCH-003' different du nom de fichier 'ARCH-002'"),
            (".archgate/adrs/GEN-001-example.md", "ADR hors du registre declare"),
        }
        expect(errors == expected, sorted(errors ^ expected))
        warnings = {(w["where"], w["message"].split(" :")[0]) for w in rep.warnings}
        expect(("docs/user/FAQ.md", "page absente de l'index docs/user/README.md") in warnings, warnings)
        expect(("docs/user/INSTALL.md", "page utilisateur qui cite un chemin src/") in warnings, warnings)
        expect(not any(w[0].startswith("docs/developer/") for w in warnings), warnings)
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("Auto-test : OK")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".", help="racine de l'application (defaut : dossier courant)")
    parser.add_argument("--json", action="store_true", help="sortie JSON")
    parser.add_argument("--self-test", action="store_true", help="auto-test du script")
    args = parser.parse_args(argv)
    if args.self_test:
        try:
            return self_test()
        except SelfTestFailure as exc:
            print("Auto-test : ECHEC — %s" % (exc,))
            return 1
    rep = run(os.path.abspath(args.root))
    if args.json:
        print(json.dumps({"errors": rep.errors, "warnings": rep.warnings}, ensure_ascii=False, indent=2))
    else:
        print_report(rep)
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
