# Gabarits des index

Un `README.md` par dossier qui contient des pages. Un index liste ses pages, chacune avec une
phrase qui dit à quel besoin elle répond ; il ne recopie pas leur contenu. Les liens sont
relatifs. Une ligne d'index ne cite que des pages qui existent : pas de lien vers une page à écrire,
la lister sous « À écrire » sans lien.

---

## `docs/README.md` — aiguillage

```markdown
# Documentation — {application}

Par où entrer, selon ce que vous voulez faire.

| Vous voulez | Lisez |
|---|---|
| installer et utiliser {application} | [user/](user/README.md) |
| compiler, tester, contribuer | [developer/](developer/README.md) |
| comprendre l'architecture et les décisions | [architecture/](architecture/README.md) |
| connaître l'état et les priorités du projet | [project/](project/README.md) |

{Ajouter ici, au plus, les trois ou quatre pages qu'un nouveau venu cherche en premier.}
```

Rien d'autre : pas de seuil de qualité, pas d'état de jalon, pas de contenu technique.

---

## `docs/user/README.md`

```markdown
# Utiliser {application}

| Page | Pour |
|---|---|
| [INSTALL.md](INSTALL.md) | installer et configurer |

## Notes de version

[release-notes/](release-notes/README.md)

## À écrire

- {pages identifiées à l'audit, sans lien}
```

---

## `docs/developer/README.md`

```markdown
# Développer {application}

| Page | Pour |
|---|---|
| [BUILD_AND_TEST.md](BUILD_AND_TEST.md) | compiler, tester, qualifier |

## Référence

[reference/](reference/README.md) — contrats machine.

## À écrire

- {…}
```

Les seuils de qualité (couverture, mutation, analyse statique), s'il y en a, vivent ici, pas dans
`docs/README.md`.

---

## `docs/architecture/README.md`

Produit par le skill `arc42-architecture` (`resources/templates/arc42-sections.md`). Ne pas le
réécrire ici.

---

## `docs/project/README.md`

```markdown
# Piloter {application}

| Dossier | Contenu |
|---|---|
| [governance/](governance/README.md) | feuille de route, état de la documentation, autorité des documents |
| [audits/](audits/README.md) | relevés d'audit datés |

## Correspondance des anciens chemins

Tenue à chaque déplacement de fichier de `docs/`. Les relevés datés citent les chemins de leur
date : cette table permet de les suivre.

| Ancien chemin | Nouveau chemin | Date |
|---|---|---|
| `docs/adr/0003-postgres.md` | `docs/architecture/adr/DATA-001-postgresql-storage.md` | AAAA-MM-JJ |
```

---

## Index d'un sous-dossier (`audits/`, `release-notes/`, `reference/`…)

```markdown
# {Titre du dossier}

| Page | Date | Objet |
|---|---|---|
| [AUDIT_securite_2026-10-01.md](AUDIT_securite_2026-10-01.md) | 2026-10-01 | {…} |
```

Ordre : du plus récent au plus ancien pour les relevés datés, alphabétique sinon.
