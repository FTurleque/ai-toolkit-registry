#!/usr/bin/env python3
"""Installe des skills du registre dans le dossier de skills de l'utilisateur, par copie.

Le depot reste la source de verite : la copie installee se verifie et se remplace, elle ne s'edite
pas. Aucun lien symbolique (ils demandent des privileges sous Windows).

Usage :
  python tools/install_skill.py install <nom> [<nom>...]    # copie, ou met a jour
  python tools/install_skill.py check <nom> [<nom>...]      # la copie correspond-elle au depot ?
  python tools/install_skill.py uninstall <nom> [<nom>...]
  python tools/install_skill.py --self-test

Options :
  --dest DIR   dossier de skills cible (defaut : ~/.claude/skills, ou $CLAUDE_CONFIG_DIR/skills)
  --root DIR   racine du registre (defaut : le depot qui contient ce script)

Fichiers livres : dans un depot Git, ceux que Git ne masque pas dans le dossier du skill (suivis, ou
non suivis et non ignores, selon `git ls-files --cached --others --exclude-standard`) ; un fichier
ignore, comme un rapport du superviseur ecrit dans `docs/rapport-supervisor/`, n'est ni copie ni
compare. Hors Git, tout le dossier. Dans les deux cas, sans caches Python (`__pycache__`,
`.pytest_cache`, `*.pyc`) ni manifeste d'installation. `check` compare la copie installee, telle
qu'elle est sur le disque, a ces fichiers livres.

Une installation anterieure modifiee a la main n'est jamais ecrasee sans sauvegarde : elle est
copiee dans `<dest>/../skills-backup/<nom>-<horodatage>/` avant d'etre remplacee ou retiree.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time

MANIFEST = ".registry-install.json"
SKILL_FILE = "SKILL.md"
SKIP_DIRS = {"__pycache__", ".pytest_cache"}
NAME = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


def inside(base: str, *parts: str) -> str:
    """Chemin sous `base`, liens resolus ; refuse tout ce qui en sortirait."""
    base = os.path.realpath(base)
    path = os.path.realpath(os.path.join(base, *parts))
    if os.path.commonpath([base, path]) != base:
        raise SystemExit("chemin refuse, hors de %s : %s" % (base, os.path.join(*parts)))
    return path


def skill_name(value: str) -> str:
    if not NAME.match(value):
        raise SystemExit("nom de skill invalide : %r (kebab-case attendu)" % value)
    return value


def default_dest() -> str:
    base = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")
    return os.path.join(base, "skills")


def find_skill(root: str, name: str) -> str:
    """Dossier source du skill : skills/<categorie>/<nom>/, reconnu a son SKILL.md."""
    base = os.path.join(root, "skills")
    matches = [inside(base, category, name) for category in sorted(os.listdir(base))
               if os.path.isfile(inside(base, category, name, SKILL_FILE))]
    if len(matches) != 1:
        raise SystemExit("skill introuvable dans le registre : %s" % name)
    return matches[0]


def skipped(rel: str) -> bool:
    """Vrai pour un cache Python ou le manifeste d'installation, jamais livres."""
    parts = rel.split("/")
    return (parts[-1] == MANIFEST or parts[-1].endswith((".pyc", ".pyo"))
            or any(part in SKIP_DIRS for part in parts[:-1]))


def git_listed(folder: str):
    """Fichiers du dossier que Git ne masque pas (suivis, ou non suivis et non ignores) ; None hors Git."""
    try:
        proc = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z", "--", "."],
                              cwd=folder, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    listed = (os.fsdecode(raw) for raw in proc.stdout.split(b"\0") if raw)
    return {rel for rel in listed if os.path.isfile(os.path.join(folder, rel))}


def walked(folder: str) -> set:
    found = set()
    for dirpath, dirnames, filenames in os.walk(folder):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        found.update(os.path.relpath(os.path.join(dirpath, name), folder).replace(os.sep, "/")
                     for name in filenames)
    return found


def hashes(folder: str, git: bool = False) -> dict:
    """{chemin relatif: sha256} des fichiers livres, hors caches et manifeste d'installation.

    Avec `git`, se limite aux fichiers que Git ne masque pas quand le dossier est dans un depot Git.
    """
    listed = git_listed(folder) if git else None
    found = {}
    for rel in sorted(walked(folder) if listed is None else listed):
        if skipped(rel):
            continue
        with open(inside(folder, rel), "rb") as fh:
            found[rel] = hashlib.sha256(fh.read()).hexdigest()
    return found


def shipped(source: str, name: str) -> dict:
    """Fichiers livres du skill source ; refuse un skill dont `SKILL.md` serait ignore par Git."""
    files = hashes(source, git=True)
    if SKILL_FILE not in files:
        raise SystemExit("%s : %s absent des fichiers livres (ignore par Git ?)" % (name, SKILL_FILE))
    return files


def read_manifest(folder: str):
    try:
        with open(inside(folder, MANIFEST), "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def skill_version(folder: str) -> str:
    path = inside(folder, "metadata.yaml")
    if not os.path.isfile(path):
        return "?"
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("version:"):
                return line.split(":", 1)[1].strip().strip("'\"")
    return "?"


def registry_commit(root: str):
    try:
        proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL, text=True)
    except OSError:
        return None
    return proc.stdout.strip() or None if proc.returncode == 0 else None


def remove_tree(path: str) -> None:
    def retry(func, target, _exc):
        os.chmod(target, stat.S_IWRITE)
        func(target)
    shutil.rmtree(path, onerror=retry)


def copy_skill(source: str, target: str, files: dict) -> None:
    for rel in files:
        destination = inside(target, rel)
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        shutil.copy2(inside(source, rel), destination)


def locally_modified(target: str, installed: dict) -> bool:
    """Vrai si la copie installee ne correspond plus a ce qui avait ete installe."""
    manifest = read_manifest(target)
    return manifest is None or manifest.get("files") != installed


def backup(dest: str, name: str, target: str) -> str:
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    path = os.path.join(os.path.dirname(os.path.abspath(dest)), "skills-backup", "%s-%s" % (name, stamp))
    shutil.copytree(target, path)
    return path


def write_manifest(root: str, source: str, target: str, name: str, files: dict) -> None:
    data = {"name": name, "version": skill_version(source), "source": "ai-toolkit-registry",
            "commit": registry_commit(root), "files": files}
    with open(inside(target, MANIFEST), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
        fh.write("\n")


def install(root: str, dest: str, name: str) -> str:
    source = find_skill(root, name)
    target = inside(dest, skill_name(name))
    wanted = shipped(source, name)
    note = ""
    if os.path.isdir(target):
        installed = hashes(target)
        if installed == wanted:
            write_manifest(root, source, target, name, wanted)
            return "%s : deja a jour (%s)" % (name, target)
        if locally_modified(target, installed):
            note = " ; ancienne copie modifiee sauvegardee dans %s" % backup(dest, name, target)
        remove_tree(target)
    copy_skill(source, target, wanted)
    write_manifest(root, source, target, name, wanted)
    return "%s : installe, version %s, %d fichiers (%s)%s" % (name, skill_version(source), len(wanted), target, note)


def check(root: str, dest: str, name: str):
    """Retourne (a_jour, message)."""
    source = find_skill(root, name)
    target = inside(dest, skill_name(name))
    if not os.path.isdir(target):
        return False, "%s : non installe dans %s" % (name, dest)
    wanted, installed = shipped(source, name), hashes(target)
    if wanted == installed:
        return True, "%s : identique au depot, version %s (%s)" % (name, skill_version(source), target)
    differing = sorted(p for p in set(wanted) | set(installed) if wanted.get(p) != installed.get(p))
    origin = "modifiee a la main depuis son installation" if locally_modified(target, installed) \
        else "en retard sur le depot"
    lines = ["%s : DIFFERENT du depot - copie %s" % (name, origin)]
    lines += ["  - %s (%s)" % (p, "absent du depot" if p not in wanted else
                              "absent de la copie" if p not in installed else "contenu different")
              for p in differing]
    return False, "\n".join(lines)


def uninstall(dest: str, name: str) -> str:
    target = inside(dest, skill_name(name))
    if not os.path.isdir(target):
        return "%s : non installe" % name
    note = ""
    if locally_modified(target, hashes(target)):
        note = " ; copie modifiee sauvegardee dans %s" % backup(dest, name, target)
    remove_tree(target)
    return "%s : retire de %s%s" % (name, dest, note)


def exits(action) -> bool:
    """Vrai si l'action se termine par un refus (SystemExit)."""
    try:
        action()
    except SystemExit:
        return True
    return False


def write_files(folder: str, files) -> None:
    for rel, text in files:
        path = os.path.join(folder, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)


def self_test_git_ignored(root: str, dest: str, skill: str, expect) -> None:
    """Dans un depot Git, un fichier ignore du skill n'est ni copie ni compare."""
    subprocess.run(["git", "init", "-q", root], check=True, stdout=subprocess.DEVNULL)
    write_files(skill, (("docs/rapport-supervisor/.gitignore", "*\n"),
                        ("docs/rapport-supervisor/rapport.md", "rapport du superviseur\n")))
    expect("check vert avec un fichier ignore par Git dans le skill", check(root, dest, "demo")[0])
    expect("reinstallation sans changement malgre le fichier ignore", "deja a jour" in install(root, dest, "demo"))
    remove_tree(os.path.join(dest, "demo"))
    install(root, dest, "demo")
    expect("fichier ignore par Git non copie", not os.path.exists(os.path.join(dest, "demo", "docs")))
    expect("check vert apres installation avec un fichier ignore", check(root, dest, "demo")[0])
    write_files(skill, ((".gitignore", "*\n"),))
    expect("skill ignore par Git refuse", exits(lambda: install(root, dest, "demo")))
    os.remove(os.path.join(skill, ".gitignore"))


def self_test() -> int:
    """Installe, modifie, reinstalle et retire un skill factice dans un dossier temporaire."""
    base = tempfile.mkdtemp(prefix="install-skill-selftest-")
    try:
        root, dest = os.path.join(base, "registry"), os.path.join(base, "home", "skills")
        skill = os.path.join(root, "skills", "development", "demo")
        write_files(skill, ((SKILL_FILE, "---\nname: demo\n---\n"), ("metadata.yaml", "version: 1.2.3\n"),
                            ("resources/tool.py", "print('v1')\n"), ("resources/__pycache__/tool.pyc", "x")))
        failures = []

        def expect(label, condition):
            if not condition:
                failures.append(label)

        expect("non installe detecte", check(root, dest, "demo")[0] is False)
        for unsafe in ("../demo", "demo/..", "..", "Demo", ""):
            expect("nom dangereux refuse : %r" % unsafe, exits(lambda: uninstall(dest, unsafe)))
        install(root, dest, "demo")
        expect("copie identique apres installation", check(root, dest, "demo")[0])
        expect("caches non copies", not os.path.exists(os.path.join(dest, "demo", "resources", "__pycache__")))
        expect("reinstallation sans changement", "deja a jour" in install(root, dest, "demo"))
        with open(os.path.join(skill, "resources", "tool.py"), "w", encoding="utf-8") as fh:
            fh.write("print('v2')\n")
        ok, message = check(root, dest, "demo")
        expect("retard sur le depot detecte", not ok and "en retard" in message)
        expect("mise a jour sans sauvegarde inutile", "sauvegardee" not in install(root, dest, "demo"))
        with open(os.path.join(dest, "demo", SKILL_FILE), "a", encoding="utf-8") as fh:
            fh.write("retouche locale\n")
        ok, message = check(root, dest, "demo")
        expect("modification manuelle detectee", not ok and "modifiee a la main" in message)
        expect("copie modifiee sauvegardee avant remplacement", "sauvegardee" in install(root, dest, "demo"))
        saved = os.listdir(os.path.join(base, "home", "skills-backup"))
        with open(os.path.join(base, "home", "skills-backup", saved[0], SKILL_FILE), encoding="utf-8") as fh:
            expect("la sauvegarde contient la retouche", "retouche locale" in fh.read())
        expect("copie identique apres remplacement", check(root, dest, "demo")[0])
        expect("hors Git, aucun fichier filtre", hashes(skill, git=True) == hashes(skill))
        git_note = "" if shutil.which("git") else " (git absent : cas du fichier ignore par Git non teste)"
        if not git_note:
            self_test_git_ignored(root, dest, skill, expect)
        uninstall(dest, "demo")
        expect("desinstallation", not os.path.exists(os.path.join(dest, "demo")))
        if failures:
            print("ECHEC - " + ", ".join(failures))
            return 1
        print("OK - installation, verification, sauvegarde et retrait se comportent comme attendu%s." % git_note)
        return 0
    finally:
        remove_tree(base)


def main(argv) -> int:
    parser = argparse.ArgumentParser(description="Installe des skills du registre par copie.")
    parser.add_argument("action", nargs="?", choices=["install", "check", "uninstall"])
    parser.add_argument("names", nargs="*", help="noms de skills")
    parser.add_argument("--dest", default=None, help="dossier de skills cible")
    parser.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    parser.add_argument("--self-test", action="store_true", help="verifie l'installateur")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.action or not args.names:
        parser.error("action et nom(s) de skill attendus")
    dest = os.path.abspath(args.dest or default_dest())
    root = os.path.abspath(args.root)
    code = 0
    for name in map(skill_name, args.names):
        if args.action == "install":
            print(install(root, dest, name))
        elif args.action == "uninstall":
            print(uninstall(dest, name))
        else:
            ok, message = check(root, dest, name)
            print(message)
            code = code or (0 if ok else 1)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
