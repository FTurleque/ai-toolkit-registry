---
id: GEN-002
title: Ne contenir que des artefacts transverses, jamais la configuration IA d'une application
domain: general
rules: false
files: ["README.md", "docs/architecture.md", "skills/**", "plugins/**", "agents/**", "commands/**", "hooks/**", "instructions/**", "mcp/**", "output-styles/**"]
---

# Ne contenir que des artefacts transverses, jamais la configuration IA d'une application

## Context

Le dépôt s'appelait `ai-skills-registry` ; il est devenu `ai-toolkit-registry` (le module IntelliJ porte encore l'ancien nom, `.idea/ai-skills-registry.iml`). La question s'est posée de l'orienter vers la **gouvernance IA** (règles d'usage, données sensibles, conformité) plutôt que de le garder comme **toolkit**.

Faits établis :

- Le [README](../../README.md) présente le dépôt comme « un registre versionné de ce qui outille Claude au quotidien », rangé par mécanisme d'exécution ([ARCH-001](ARCH-001-storage-by-mechanism.md)).
- [instructions/README.md](../../instructions/README.md) ne prévoit que des **gabarits** : « Copier le gabarit à la racine du dépôt cible et le remplir. »
- Le mainteneur a indiqué le 2026-10-22 que chaque application possède déjà sa propre configuration IA, et que le registre ne doit porter que ce qui est global.

**Alternatives (analyse d'aujourd'hui) :**

- *Dépôt de gouvernance IA* : il imposerait des règles à des projets dont la configuration vit ailleurs ; il n'aurait rien à appliquer ici, et mélangerait une offre (on choisit d'installer) et une obligation (on doit se conformer).
- *Centraliser la configuration des applications ici* : deux sources pour un même `CLAUDE.md`, désynchronisées dès la première modification locale.

## Decision

**Statut : proposée (2026-10-22).** En attente d'acceptation par le mainteneur. Responsable : Fabrice Turleque.

- Le registre est un **toolkit** : il ne contient que des artefacts transverses, réutilisables par plusieurs projets.
- La configuration IA propre à une application (son `CLAUDE.md`, son `AGENTS.md`, ses `settings.json`, ses règles) MUST vivre dans le dépôt de cette application, jamais ici.
- `instructions/` MUST ne contenir que des gabarits génériques ; un exemple rempli (`examples/`) illustre le gabarit, il n'est pas la configuration de référence d'un projet.
- Une gouvernance IA (politique d'usage, données sensibles, conformité) MUST NOT être hébergée dans ce dépôt ; s'il en faut une, elle vit dans un dépôt ou un document distinct, que le registre peut référencer.
- La configuration de **ce** dépôt (`.claude/`) n'est pas concernée : c'est la configuration d'une application comme une autre, ici le registre lui-même.

Périmètre : le contenu de tous les dossiers de type, le README racine.

## Do's and Don'ts

### Do
- Se demander, avant d'ajouter un artefact : « servira-t-il à au moins un autre projet tel quel, ou après remplissage d'un gabarit ? »
- Extraire la partie générique d'une configuration de projet en gabarit, et laisser le reste dans le projet.

### Don't
- Ne pas déposer ici le `CLAUDE.md` d'une application « pour l'avoir sous la main ».
- Ne pas ajouter un type d'artefact « policy » ou « governance » au schéma.

## Consequences

### Positive
- Une seule source pour la configuration de chaque application : la sienne.
- Le registre reste une offre : rien n'y est obligatoire pour les projets qui ne l'installent pas.

### Negative
- Une bonne pratique découverte dans une application n'arrive ici que si quelqu'un l'extrait en gabarit ou en skill.

### Risks
- Le jour où une gouvernance IA devient nécessaire, la tentation sera de la loger ici parce que le dépôt existe déjà. Cette décision devra alors être remplacée explicitement, pas contournée.

## Compliance and Enforcement

### Automated Enforcement
- Aucune. Ni `tools/validate.py` ni Archgate ne peuvent distinguer un gabarit d'une configuration de projet.

### Manual Enforcement
- Relecture de PR : tout ajout dans `instructions/` ou tout fichier qui nomme une application précise est examiné sous l'angle de cette décision.

## References

- [README.md](../../README.md) — section « Portée »
- [instructions/README.md](../../instructions/README.md)
- [ARCH-001](ARCH-001-storage-by-mechanism.md) — rangement par mécanisme
- [GEN-001](GEN-001-claude-only-declared-surfaces.md) — périmètre des surfaces
