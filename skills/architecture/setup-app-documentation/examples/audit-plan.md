# Exemple — rapport d'audit (phase 1)

Application fictive `gestion-conges` : API Quarkus, front Angular. `docs/` contient six fichiers en
vrac et un dossier `docs/adr/` ; deux ADR traînent aussi dans `.archgate/adrs/`. Archgate 0.60.0 et
le plugin `code-supervisor` sont installés sur le poste. Rapport rendu avant toute écriture.

```markdown
## Documentation — audit de gestion-conges

### Outils
- Archgate : installé (0.60.0) · projet configuré : oui · registre : .archgate/adrs/ (pas de paths.adrs)
- Superviseur : code-supervisor (plugin) · log_subdir : — (défaut docs/rapport-supervisor, dossier présent)
- Skill arc42-architecture : installé

### Constat
Deux registres d'ADR (docs/adr/ au format Markdown simple, .archgate/adrs/ au format Archgate).
docs/INSTALL.md mêle installation et compilation. Aucun index, aucun aiguillage.
docs/API.md est cité par .github/workflows/ci.yml (vérification de présence).

### Plan de rangement
| # | Fichier actuel | Destination | Lecteur | Cité par | Action |
|---|---|---|---|---|---|
| 1 | docs/INSTALL.md (partie installation) | docs/user/INSTALL.md | utilisateur | README.md:12 | git mv + citation |
| 2 | docs/INSTALL.md (partie compilation) | docs/developer/BUILD_AND_TEST.md | développeur | — | page coupée |
| 3 | docs/API.md | docs/developer/reference/API.md | développeur | ci.yml:41 | git mv + ci.yml |
| 4 | docs/adr/0001-keycloak.md | docs/architecture/adr/SEC-001-keycloak-authentication.md | décision | — | conversion Archgate |
| 5 | .archgate/adrs/ARCH-001-hexagonal.md (+ .rules.ts) | docs/architecture/adr/ | décision | — | git mv, id inchangé |
| 6 | docs/audit-securite-2026-03.md | docs/project/audits/AUDIT_securite_2026-03-15.md | pilotage | — | git mv, prose intacte |

### Pages à créer
docs/README.md, docs/user/README.md, docs/developer/README.md, docs/project/README.md (table de
correspondance), docs/project/audits/README.md. docs/architecture/ : phases d'arc42-architecture.

### Configuration
- .claude/rules/documentation.md : créer (aucune règle de documentation existante)
- Archgate : paths.adrs → docs/architecture/adr ; .archgate/lint/ présent ; .gitignore +
  docs/architecture/rules.d.ts. Avant : 2 ADR, total 1 règle — à retrouver après.
- Superviseur : .claude/supervisor.config.json, log_subdir docs/project/rapport-supervisor ;
  l'ancien docs/rapport-supervisor/ (non versionné) pourra être supprimé.

### Questions ouvertes
- Couper docs/INSTALL.md en deux pages (lignes 1-40 installation, 41-95 compilation) ?
- docs/adr/0001-keycloak.md devient SEC-001 : créer le domaine `security` (préfixe SEC) avec
  `archgate adr domain add`, ou le classer en ARCH ?
```

> **Prêt à mettre en place la documentation. Confirmez pour continuer (phase 2).**
