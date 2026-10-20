"""Bac à sable des tests : dépôts temporaires et remotes bare locaux, isolés de la configuration du poste."""
from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys
import tempfile

SKILLS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PUBLISH = os.path.join(SKILLS, "publish-git-submodule", "resources", "scripts", "publish.py")
INSTALL = os.path.join(SKILLS, "install-git-submodule", "resources", "scripts", "install.py")
UPDATE = os.path.join(SKILLS, "install-git-submodule", "resources", "scripts", "update.py")
COMMON = os.path.join(SKILLS, "git-submodule-common", "resources", "scripts", "submodule_common.py")

# Fichier de configuration globale du bac à sable : aucune maintenance automatique. Git la lance
# après commit, fetch ou push (y compris receive-pack sur le remote bare), détachée en arrière-plan ;
# ce processus survivant modifie .git/objects pendant la suppression du bac à sable. Ces réglages
# vivent dans ce fichier, pas dans GIT_CONFIG_COUNT, parce que git retire GIT_CONFIG_COUNT de
# l'environnement du receive-pack d'un remote local. Si une maintenance passait malgré tout, elle
# resterait au premier plan, donc attendue par la commande qui l'a lancée.
GLOBAL_CONFIG = """[maintenance]
    auto = false
    autoDetach = false
[gc]
    auto = 0
    autoDetach = false
[receive]
    autoGC = false
"""


class Sandbox:
    def __init__(self):
        self.base = tempfile.mkdtemp(prefix="submodule-sync-test-")
        config = os.path.join(self.base, "gitconfig")
        with open(config, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(GLOBAL_CONFIG)
        empty = os.path.join(self.base, "excludes")
        open(empty, "w").close()
        env = dict(os.environ)
        for key in list(env):
            if key.startswith(("GIT_", "GITHUB_", "SUBMODULE_")) or key in ("GH_TOKEN", "CI"):
                del env[key]
        env.update(
            GIT_CONFIG_GLOBAL=config, GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0",
            GIT_AUTHOR_NAME="Test", GIT_AUTHOR_EMAIL="test@example.invalid",
            GIT_COMMITTER_NAME="Test", GIT_COMMITTER_EMAIL="test@example.invalid",
            # Les sous-modules clonés depuis un chemin local sont refusés par défaut depuis git 2.38.1.
            GIT_CONFIG_COUNT="3",
            GIT_CONFIG_KEY_0="protocol.file.allow", GIT_CONFIG_VALUE_0="always",
            GIT_CONFIG_KEY_1="core.autocrlf", GIT_CONFIG_VALUE_1="false",
            # Le fichier d'exclusions personnel du poste ne doit pas décider de ce qui est commité ici.
            GIT_CONFIG_KEY_2="core.excludesFile", GIT_CONFIG_VALUE_2=empty.replace(os.sep, "/"),
            PYTHONIOENCODING="utf-8")
        self.env = env

    def close(self):
        def retry(func, path, exc):
            error = exc[1] if isinstance(exc, tuple) else exc
            if isinstance(error, FileNotFoundError):
                return
            # Windows : les objets git sont en lecture seule, le droit d'écriture débloque la suppression.
            os.chmod(path, stat.S_IWRITE)
            func(path)
        if sys.version_info >= (3, 12):
            shutil.rmtree(self.base, onexc=retry)
        else:
            shutil.rmtree(self.base, onerror=retry)

    def path(self, *parts):
        return os.path.join(self.base, *parts)

    def git(self, cwd, *args, check=True, env=None):
        proc = subprocess.run(["git"] + list(args), cwd=cwd, env=env or self.env, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
        if check and proc.returncode != 0:
            raise AssertionError("git %s : %s" % (" ".join(args), proc.stderr))
        return proc.stdout.strip()

    def bare(self, name):
        path = self.path(name + ".git")
        self.git(self.base, "init", "-q", "--bare", "-b", "main", path)
        return path

    def clone(self, remote, name):
        path = self.path(name)
        self.git(self.base, "clone", "-q", remote, path)
        self.git(path, "checkout", "-q", "-B", "main")
        return path

    def write(self, repo, rel, text):
        full = os.path.join(repo, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        return full

    def read(self, repo, rel):
        with open(os.path.join(repo, rel), "r", encoding="utf-8") as fh:
            return fh.read()

    def commit(self, repo, message, push=True):
        self.git(repo, "add", "-A")
        self.git(repo, "commit", "-q", "-m", message)
        if push:
            self.git(repo, "push", "-q", "origin", "HEAD:refs/heads/main")
        return self.git(repo, "rev-parse", "HEAD")

    def project(self, name, files):
        """Remote bare + clone de travail, avec un premier commit poussé."""
        remote = self.bare(name)
        repo = self.clone(remote, name)
        for rel, text in files.items():
            self.write(repo, rel, text)
        self.commit(repo, "initial")
        return remote, repo

    def script(self, script, cwd, *args, env=None):
        merged = dict(self.env)
        merged.update(env or {})
        return subprocess.run([sys.executable, script] + list(args), cwd=cwd, env=merged,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                              encoding="utf-8", errors="replace")

    def remote_tree(self, remote, ref):
        """Chemins de tous les fichiers d'une branche du remote."""
        out = self.git(remote, "ls-tree", "-r", "--name-only", "-z", ref)
        return sorted(p for p in out.split("\0") if p)

    def remote_sha(self, remote, branch):
        return self.git(remote, "rev-parse", "-q", "--verify", "refs/heads/" + branch, check=False)
