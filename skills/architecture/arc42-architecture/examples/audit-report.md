# Exemple — rapport d'audit (extrait)

Application fictive `gestion-conges` : API Quarkus, base PostgreSQL, front Angular, déploiement
Kubernetes. Le dépôt a un `README.md`, un dossier `docs/` avec un schéma `.drawio` et deux ADR dans
`docs/adr/`. Extrait du rapport rendu en phase 1, avant toute écriture.

```markdown
## Audit de conformité arc42 — gestion-conges

### Verdict global
Conformité : 1/12 sections conformes — 3 partielles, 1 divergente, 7 absentes
Outillage : arc42 non · C4 non · ADR oui (2, hors gabarit) · Mermaid non

### Détail par section
| # | Section | Verdict | Preuve / manque | Fichiers concernés |
|---|---------|---------|-----------------|--------------------|
| 7 | Vue de déploiement | ⚠️ | Le schéma montre une VM unique ; le dépôt déploie 3 pods et un CronJob | docs/archi.drawio, deploy/k8s/*.yaml |
| 1 | Introduction et objectifs | 🟡 | Mission dans le README, aucun objectif qualité priorisé | README.md:3 |
| 9 | Décisions | 🟡 | 2 ADR sans statut ni conséquences | docs/adr/001-postgres.md |
| 12 | Glossaire | ❌ | Aucune trace | — |

### Hypothèses à valider
| Hypothèse | Preuve nécessaire | Qui peut trancher |
|---|---|---|
| Le CronJob `solde-annuel` est le seul traitement batch | Liste des CronJobs en production | Équipe d'exploitation |

### ADR à créer
- Authentification déléguée à Keycloak (`application.properties:18`), non tracée.
```

> **Prêt à intégrer / compléter la documentation arc42. Confirmez pour continuer (Phase 2).**
