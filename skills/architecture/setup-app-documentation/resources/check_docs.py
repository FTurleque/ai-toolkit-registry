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
  - page de docs/user/ qui cite un chemin src/, une commande de build ou un SHA ;
  - fichier qui sort de la racine par un lien symbolique : il n'est pas lu.

Bibliotheque standard seulement (Python 3.8+). Lecture seule, confinee sous --root.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile

DOCS = "docs"
DOCS_PREFIX = DOCS + "/"
INDEX = "README.md"
ARCHGATE = ".archgate"
LEGACY_REGISTRY = ARCHGATE + "/adrs"
TOP_DIRS = {"user", "developer", "architecture", "project"}
ADR_DIR = ("architecture", "adr")
ADR_PREFIX = DOCS_PREFIX + "/".join(ADR_DIR) + "/"
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
        entry = {"where": where, "message": message}
        if entry not in self.warnings:  # un fichier lu par plusieurs controles ne compte qu'une fois
            self.warnings.append(entry)


def posix(path):
    return path.replace(os.sep, "/")


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


def local_target(target):
    """Chemin d'un lien relatif, sans ancre ni requete ; None pour un lien externe ou une ancre."""
    if is_external(target):
        return None
    return target.split("#", 1)[0].split("?", 1)[0] or None


def front_matter_id(text):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    match = re.search(r"^id:\s*['\"]?([^'\"\s]+)", text[3:end], re.M)
    return match.group(1) if match else None


class Checker:
    """Controles d'une application ; toute lecture reste sous sa racine."""

    def __init__(self, root):
        self.root = os.path.realpath(root)
        self.docs = os.path.join(self.root, DOCS)
        self.rep = Report()

    # -- acces aux fichiers -------------------------------------------------------------

    def rel(self, path):
        return posix(os.path.relpath(path, self.root))

    def inside(self, path):
        real = os.path.realpath(path)
        try:
            return os.path.commonpath([self.root, real]) == self.root
        except ValueError:  # autre lecteur Windows : hors de la racine
            return False

    def read(self, path):
        """Texte du fichier, ou "" s'il sort de la racine ou ne se lit pas : il n'est pas lu."""
        if not self.inside(path):
            self.rep.warn(self.rel(path), "sort de la racine par un lien symbolique : non lu")
            return ""
        try:
            with open(os.path.realpath(path), "r", encoding="utf-8", errors="replace") as fh:
                return fh.read()
        except OSError as exc:
            self.rep.warn(self.rel(path), "illisible (%s) : non lu" % exc.__class__.__name__)
            return ""

    def walk(self):
        for current, dirs, files in os.walk(self.docs):
            rel = os.path.relpath(current, self.docs)
            parts = () if rel == "." else tuple(posix(rel).split("/"))
            dirs[:] = sorted(d for d in dirs if not (parts == ("project",) and d in LOCAL_DIRS))
            yield parts, dirs, sorted(files)

    # -- controles ----------------------------------------------------------------------

    def check_docs_entry(self, name):
        path = os.path.join(self.docs, name)
        if os.path.isfile(path) and name != INDEX:
            self.rep.error(DOCS_PREFIX + name, "fichier a la racine de docs/ : seul README.md y a sa place")
        elif os.path.isdir(path) and name not in TOP_DIRS:
            self.rep.error(DOCS_PREFIX + name + "/",
                           "dossier de premier niveau non prevu (user, developer, architecture, project)")

    def check_structure(self):
        for name in sorted(os.listdir(self.docs)):
            self.check_docs_entry(name)
        if not os.path.isfile(os.path.join(self.docs, INDEX)):
            self.rep.error(DOCS_PREFIX + INDEX, "aiguillage absent")

    def check_page_links(self, folder, name):
        rel = self.rel(os.path.join(folder, name))
        for target in links_of(self.read(os.path.join(folder, name))):
            clean = local_target(target)
            if clean and not os.path.exists(os.path.normpath(os.path.join(folder, clean))):
                self.rep.error(rel, "lien casse : %s" % target)

    def check_links(self):
        for parts, _dirs, files in self.walk():
            folder = os.path.join(self.docs, *parts)
            for name in (f for f in files if f.endswith(".md")):
                self.check_page_links(folder, name)

    def check_folder_index(self, folder, rel, pages, children):
        index = os.path.join(folder, INDEX)
        if not os.path.isfile(index):
            self.rep.warn(rel, "pas de README.md d'index")
            return
        index_text = self.read(index)
        linked = {posix(os.path.normpath(t)) for t in map(local_target, links_of(index_text)) if t}
        for page in pages:
            if page not in linked and page not in index_text:
                self.rep.warn(rel + page, "page absente de l'index %s%s" % (rel, INDEX))
        for child in children:
            if not any(link == child or link.startswith(child + "/") for link in linked):
                self.rep.warn(rel + child + "/", "sous-dossier absent de l'index %s%s" % (rel, INDEX))

    def check_indexes(self):
        """Index des dossiers de pages ; docs/architecture/ releve du skill arc42-architecture."""
        for parts, dirs, files in self.walk():
            if not parts or parts[0] == "architecture":
                continue
            folder = os.path.join(self.docs, *parts)
            pages = [f for f in files if f.endswith(".md") and f != INDEX]
            children = [d for d in dirs if os.listdir(os.path.join(folder, d))]
            if pages or children:
                self.check_folder_index(folder, DOCS_PREFIX + "/".join(parts) + "/", pages, children)

    def check_adr_entry(self, adr, name):
        rel = ADR_PREFIX + name
        path = os.path.join(adr, name)
        if os.path.isdir(path):
            self.rep.warn(rel + "/", "sous-dossier dans le registre : Archgate ne le lit pas")
            return
        if not name.endswith(".md"):
            return  # Archgate ne lit que les .md : .gitkeep, .rules.ts, tsconfig.json des regles
        match = ADR_FILE.match(name)
        if not match:
            self.rep.error(rel, "pas une ADR (<PREFIXE>-<NNN>-<slug>.md) : Archgate la signalerait dans unparsedAdrs")
            return
        declared = front_matter_id(self.read(path))
        if declared != match.group(1):
            self.rep.error(rel, "id du front matter %r different du nom de fichier %r" % (declared, match.group(1)))

    def declared_registry(self):
        """Registre declare par .archgate/config.json, ou None sans configuration lisible."""
        config = os.path.join(self.root, ARCHGATE, "config.json")
        if not os.path.isfile(config):
            return None
        try:
            paths = json.loads(self.read(config) or "{}").get("paths") or {}
        except ValueError:
            self.rep.error(self.rel(config), "JSON illisible")
            return None
        return paths.get("adrs") or LEGACY_REGISTRY

    def check_archgate_layout(self, registry):
        if posix(registry).strip("/") == LEGACY_REGISTRY:
            return
        legacy = os.path.join(self.root, ARCHGATE, "adrs")
        if os.path.isdir(legacy):
            for name in sorted(n for n in os.listdir(legacy) if n.endswith(".md")):
                self.rep.error(LEGACY_REGISTRY + "/" + name, "ADR hors du registre declare (%s)" % registry)
        elif not os.path.isdir(os.path.join(self.root, ARCHGATE, "lint")):
            self.rep.error(ARCHGATE + "/", "ni lint/ ni adrs/ : Archgate ne reconnaitra pas le projet")

    def check_adr_registry(self):
        adr = os.path.join(self.docs, *ADR_DIR)
        if os.path.isdir(adr):
            for name in sorted(os.listdir(adr)):
                self.check_adr_entry(adr, name)
        registry = self.declared_registry()
        if registry is not None:
            self.check_archgate_layout(registry)

    def check_user_page(self, path):
        text = self.read(path)
        for pattern, label in USER_SMELLS:
            if pattern.search(text):
                self.rep.warn(self.rel(path), "page utilisateur qui cite un %s : contenu developer/ ou project/" % label)

    def check_user_pages(self):
        user = os.path.join(self.docs, "user")
        for current, _dirs, files in os.walk(user):
            if "release-notes" in posix(os.path.relpath(current, user)).split("/"):
                continue
            for name in (f for f in sorted(files) if f.endswith(".md")):
                self.check_user_page(os.path.join(current, name))

    def run(self):
        if not os.path.isdir(self.docs):
            self.rep.error(DOCS_PREFIX, "dossier absent")
            return self.rep
        self.check_structure()
        self.check_links()
        self.check_indexes()
        self.check_adr_registry()
        self.check_user_pages()
        return self.rep


def run(root):
    return Checker(root).run()


def print_report(rep):
    for level, items in (("ERREUR", rep.errors), ("AVERTISSEMENT", rep.warnings)):
        for item in items:
            print("%s  %s : %s" % (level, item["where"], item["message"]))
    print("\n%d erreur(s), %d avertissement(s)." % (len(rep.errors), len(rep.warnings)))


# --------------------------------------------------------------------------- auto-test

USER_INSTALL = "docs/user/INSTALL.md"


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


def build_clean_tree(base):
    write(base, "docs/README.md", "[user](user/README.md) [dev](developer/README.md)\n")
    write(base, "docs/user/README.md", "[Installer](INSTALL.md)\n")
    write(base, USER_INSTALL, "Lancer `app`.\n")
    write(base, "docs/developer/README.md", "[Build](BUILD.md)\n")
    write(base, "docs/developer/BUILD.md", "```\n[pas un lien](absent.md)\n```\n./mvnw verify\n")
    write(base, "docs/architecture/adr/ARCH-001-hexagonal.md", "---\nid: ARCH-001\n---\n")
    write(base, "docs/architecture/adr/tsconfig.json", "{}")
    write(base, ".archgate/config.json", '{"paths": {"adrs": "docs/architecture/adr"}}')
    write(base, ".archgate/lint/.gitkeep")
    write(base, "docs/project/rapport-supervisor/rapport.md", "[casse](nulle-part.md)\n")


def break_tree(base):
    write(base, "docs/NOTES.md")
    write(base, "docs/adr/0001-x.md")
    write(base, USER_INSTALL, "Voir [build](../developer/ABSENT.md), src/Main.java\n")
    write(base, "docs/user/FAQ.md")
    write(base, "docs/architecture/adr/README.md")
    write(base, "docs/architecture/adr/ARCH-002-db.md", "---\nid: ARCH-003\n---\n")
    write(base, ".archgate/adrs/GEN-001-example.md", "---\nid: GEN-001\n---\n")


def check_symlink_confinement(base):
    """Un lien symbolique vers l'exterieur n'est pas lu. Saute si le systeme refuse les liens."""
    outside = tempfile.mkdtemp(prefix="check-docs-outside-")
    try:
        write(outside, "secret.md", "[lien](n-importe-ou.md)\n")
        link = os.path.join(base, "docs", "user", "LEAK.md")
        try:
            os.symlink(os.path.join(outside, "secret.md"), link)
        except (OSError, NotImplementedError):
            return
        dangling = os.path.join(base, "docs", "user", "DANGLING.md")
        os.symlink(os.path.join(base, "docs", "user", "absent.md"), dangling)
        rep = run(base)
        expect(not any(e["where"] == "docs/user/LEAK.md" for e in rep.errors), rep.errors)
        for name in ("LEAK.md", "DANGLING.md"):
            expect(any(w["where"] == "docs/user/" + name and "non lu" in w["message"] for w in rep.warnings),
                   rep.warnings)
        os.remove(link)
        os.remove(dangling)
    finally:
        shutil.rmtree(outside, ignore_errors=True)


def self_test():
    base = tempfile.mkdtemp(prefix="check-docs-")
    try:
        build_clean_tree(base)
        clean = run(base)
        expect(not clean.errors and not clean.warnings, (clean.errors, clean.warnings))
        check_symlink_confinement(base)

        break_tree(base)
        rep = run(base)
        errors = {(e["where"], e["message"].split(" :")[0].split(" (")[0]) for e in rep.errors}
        expected = {
            ("docs/NOTES.md", "fichier a la racine de docs/"),
            ("docs/adr/", "dossier de premier niveau non prevu"),
            (USER_INSTALL, "lien casse"),
            ("docs/architecture/adr/README.md", "pas une ADR"),
            ("docs/architecture/adr/ARCH-002-db.md", "id du front matter 'ARCH-003' different du nom de fichier 'ARCH-002'"),
            (".archgate/adrs/GEN-001-example.md", "ADR hors du registre declare"),
        }
        expect(errors == expected, sorted(errors ^ expected))
        warnings = {(w["where"], w["message"].split(" :")[0]) for w in rep.warnings}
        expect(("docs/user/FAQ.md", "page absente de l'index docs/user/README.md") in warnings, warnings)
        expect((USER_INSTALL, "page utilisateur qui cite un chemin src/") in warnings, warnings)
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
    rep = run(args.root)
    if args.json:
        print(json.dumps({"errors": rep.errors, "warnings": rep.warnings}, ensure_ascii=False, indent=2))
    else:
        print_report(rep)
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
