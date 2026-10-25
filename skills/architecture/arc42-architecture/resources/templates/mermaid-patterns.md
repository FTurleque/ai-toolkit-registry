# Patterns Mermaid — C4 et UML

Patterns de référence pour tous les diagrammes de la documentation arc42.

**Notation retenue** :

| Niveau / vue | Type de diagramme Mermaid |
|---|---|
| C4 niveau 1 — Contexte | `C4Context` |
| C4 niveau 2 — Conteneurs | `C4Container` |
| C4 niveau 3 — Composants | `C4Component` |
| Vue d'exécution (arc42 §6) | `sequenceDiagram` |
| Vue de déploiement (arc42 §7) | `C4Deployment` |
| Niveau code, zones critiques (arc42 §5.3) | `classDiagram` |

La syntaxe C4 native de Mermaid est utilisée pour les quatre vues C4 : c'est la seule notation C4
réelle offerte par Mermaid, et reproduire C4 à la main avec des `flowchart` produirait une notation
maison que personne ne reconnaîtrait.

> ⚠️ **Prérequis à vérifier une fois par dépôt** : Mermaid classe les diagrammes `C4*` comme
> expérimentaux — le rendu dépend de la version embarquée par le visualiseur (GitLab, IDE, export).
> Avant d'adopter ces patterns dans une application, **afficher un diagramme C4 dans le visualiseur
> réellement utilisé par l'équipe** et le consigner dans `docs/architecture/README.md`.
> Si le visualiseur ne le rend pas : le signaler à l'équipe et trancher explicitement. Ne pas
> improviser une notation de remplacement diagramme par diagramme — un dépôt qui mélange deux
> notations C4 est illisible.

## Stéréotypes

En syntaxe C4 native, le stéréotype est porté par le **type d'élément**, que Mermaid affiche
lui-même sur la forme (`[Person]`, `[Container: Quarkus]`, `[Component]`…) :

| Stéréotype attendu | Élément C4 à employer |
|---|---|
| `«Person»` | `Person(...)` · `Person_Ext(...)` |
| `«Software System»` | `System(...)` · `System_Ext(...)` |
| `«Container»` | `Container(...)` · `Container_Ext(...)` |
| `«database»` | `ContainerDb(...)` · `ComponentDb(...)` · `SystemDb(...)` |
| file d'attente | `ContainerQueue(...)` · `SystemQueue(...)` |
| `«Component»` | `Component(...)` · `Component_Ext(...)` |
| `«node»` | `Deployment_Node(...)` |

`«interface»` et `«adapter»` n'ont pas d'équivalent C4 : les écrire **en préfixe du libellé** —
`Component(repo, "«interface» DossierRepository", …)`. Au niveau code, `classDiagram` les porte
nativement avec `<<interface>>`.

Ordre des paramètres, à respecter :
`Person(alias, "Nom", "Responsabilité")` ·
`Container(alias, "Nom", "Technologie", "Responsabilité")` ·
`Rel(source, cible, "Action", "Protocole")`

---

## 1 · C4 Niveau 1 — Contexte

**Type** : `C4Context` · **Portée** : le système et son environnement immédiat

```mermaid
C4Context
    title Diagramme de contexte — Application RH

    Person(agentRH, "Agent RH", "Gère les dossiers du personnel")
    Person(gestionnaire, "Gestionnaire paie", "Valide et transmet la paie")

    System(applicationRH, "Application RH", "Gestion administrative des agents")

    System_Ext(annuaire, "Annuaire d'entreprise", "Référentiel d'identités")
    System_Ext(moteurPaie, "Moteur de paie", "Calcule les bulletins")
    System_Ext(ged, "GED", "Archive les pièces justificatives")

    Rel(agentRH, applicationRH, "Consulte et met à jour les dossiers", "HTTPS")
    Rel(gestionnaire, applicationRH, "Valide les campagnes de paie", "HTTPS")
    Rel(applicationRH, annuaire, "Authentifie les utilisateurs", "LDAPS")
    Rel(applicationRH, moteurPaie, "Transmet les éléments variables", "REST")
    Rel(applicationRH, ged, "Dépose les justificatifs", "SFTP")
```

**Règles pour ce niveau** : aucun composant interne, aucune technologie interne. Un lecteur non
technique doit pouvoir le comprendre.

---

## 2 · C4 Niveau 2 — Conteneurs

**Type** : `C4Container` · **Portée** : intérieur du système, sans descendre aux composants

```mermaid
C4Container
    title Diagramme de conteneurs — Application RH

    Person(agentRH, "Agent RH", "Gère les dossiers du personnel")
    System_Ext(annuaire, "Annuaire d'entreprise", "Référentiel d'identités")
    System_Ext(moteurPaie, "Moteur de paie", "Calcule les bulletins")

    Container_Boundary(applicationRH, "Application RH") {
        Container(ihm, "IHM Web", "Java / JSP", "Présentation et saisie")
        Container(service, "Service métier", "Quarkus", "Règles de gestion RH")
        Container(batch, "Batch nocturne", "Java", "Consolidations et exports")
        ContainerDb(baseRH, "Base RH", "PostgreSQL", "Dossiers agents et historiques")
    }

    Rel(agentRH, ihm, "Utilise", "HTTPS")
    Rel(ihm, service, "Appelle", "REST/JSON")
    Rel(service, baseRH, "Lit et écrit", "JDBC")
    Rel(batch, baseRH, "Lit et écrit", "JDBC")
    Rel(service, annuaire, "Authentifie", "LDAPS")
    Rel(batch, moteurPaie, "Transmet les éléments variables", "REST")
```

**Règles** : un conteneur = une unité **déployable séparément**. Si deux « conteneurs » partent
toujours dans le même artefact, ce sont des composants, pas des conteneurs.

---

## 3 · C4 Niveau 3 — Composants

**Type** : `C4Component` · **Portée** : intérieur du conteneur `Service métier` **uniquement**

À produire seulement pour les conteneurs dont la complexité interne le justifie.

```mermaid
C4Component
    title Diagramme de composants — conteneur Service métier

    Container(ihm, "IHM Web", "Java / JSP", "Présentation et saisie")
    ContainerDb(baseRH, "Base RH", "PostgreSQL", "Dossiers agents et historiques")
    System_Ext(moteurPaie, "Moteur de paie", "Calcule les bulletins")

    Container_Boundary(service, "Service métier [Quarkus]") {
        Component(ressource, "Ressource REST Dossier", "JAX-RS", "Expose les opérations dossier")
        Component(appService, "Service applicatif Dossier", "CDI", "Orchestre les cas d'usage")
        Component(domaine, "Domaine Dossier", "Java", "Porte les règles d'éligibilité")
        Component(repo, "«interface» DossierRepository", "Java", "Contrat de persistance")
        Component(adaptJdbc, "«adapter» DossierRepositoryJdbc", "JDBC", "Traduit vers SQL")
        Component(adaptPaie, "«adapter» ClientPaie", "REST client", "Traduit vers l'API paie")
    }

    Rel(ihm, ressource, "Appelle", "REST/JSON")
    Rel(ressource, appService, "Délègue")
    Rel(appService, domaine, "Applique les règles")
    Rel(appService, repo, "Dépend de")
    Rel(adaptJdbc, repo, "Implémente")
    Rel(adaptJdbc, baseRH, "Interroge", "JDBC")
    Rel(appService, adaptPaie, "Utilise")
    Rel(adaptPaie, moteurPaie, "Appelle", "REST")
```

**Règles** : ne jamais mélanger conteneurs internes et composants dans un même diagramme. Les
éléments extérieurs au conteneur audité restent en **bord** du diagramme, hors de la frontière.

---

## 4 · Vue d'exécution — scénario nominal

**Type** : UML `sequenceDiagram` · **Portée** : création d'un dossier agent

```mermaid
sequenceDiagram
    autonumber
    actor agentRH as «Person» Agent RH
    participant ihm as «Container» IHM Web
    participant service as «Container» Service métier
    participant baseRH as «database» Base RH

    agentRH->>ihm: Soumet le formulaire de création
    ihm->>service: POST /dossiers (REST/JSON)
    service->>service: Valide les règles d'éligibilité
    service->>baseRH: INSERT dossier (JDBC, transaction)
    baseRH-->>service: Identifiant généré
    service-->>ihm: 201 Created + identifiant
    ihm-->>agentRH: Confirmation et redirection vers le dossier
```

Les noms de participants reprennent **à l'identique** ceux de `C4Container`, stéréotype compris —
c'est ce qui permet de passer d'une vue statique à une vue dynamique sans se demander qui est qui.

---

## 5 · Vue d'exécution — scénario d'erreur

**Type** : UML `sequenceDiagram` · **Portée** : indisponibilité du moteur de paie

```mermaid
sequenceDiagram
    autonumber
    participant batch as «Container» Batch nocturne
    participant moteurPaie as «Software System» Moteur de paie
    participant baseRH as «database» Base RH

    batch->>baseRH: Lit les éléments variables du mois
    baseRH-->>batch: Lot de N enregistrements
    batch->>moteurPaie: POST /elements-variables (REST)

    alt Réponse en erreur ou timeout
        moteurPaie--xbatch: Timeout après 30 s
        batch->>batch: 3 tentatives, backoff exponentiel
        batch->>baseRH: Marque le lot « à rejouer »
        batch->>batch: Journalise en ERROR avec l'identifiant de lot
        Note over batch: Aucune donnée perdue — le lot reste rejouable
    else Réponse acceptée
        moteurPaie-->>batch: 202 Accepted
        batch->>baseRH: Marque le lot « transmis »
    end
```

**Règles** : un scénario d'erreur montre la **détection**, la **propagation**, l'**effet observable**
et la **reprise**. Un `alt` qui s'arrête à « erreur » ne documente rien.

---

## 6 · Vue d'exécution — scénario d'exploitation

**Type** : UML `sequenceDiagram` · **Portée** : démarrage du service métier

```mermaid
sequenceDiagram
    autonumber
    participant orchestrateur as «node» Orchestrateur
    participant service as «Container» Service métier
    participant baseRH as «database» Base RH
    participant annuaire as «Software System» Annuaire d'entreprise

    orchestrateur->>service: Démarre le conteneur
    service->>service: Charge la configuration
    service->>baseRH: Vérifie la connexion et la version du schéma
    baseRH-->>service: Schéma en version attendue
    service->>annuaire: Vérifie la connexion LDAPS
    annuaire-->>service: Liaison établie
    service-->>orchestrateur: Sonde de vivacité OK
    Note over orchestrateur,service: Trafic routé vers l'instance seulement après la sonde
```

---

## 7 · Vue de déploiement

**Type** : `C4Deployment` · **Portée** : environnement de production

Les `Deployment_Node` s'imbriquent : zone réseau → machine → runtime → conteneur.

```mermaid
C4Deployment
    title Diagramme de déploiement — Application RH, production

    Deployment_Node(posteUtilisateur, "Poste utilisateur", "Windows") {
        Deployment_Node(navigateur, "Navigateur", "Chrome, Firefox") {
            Container(ihmClient, "IHM Web", "HTML / JS", "Interface utilisateur")
        }
    }

    Deployment_Node(zoneDmz, "Zone réseau DMZ", "VLAN filtré") {
        Deployment_Node(serveurProxy, "Reverse proxy", "nginx") {
            Container(proxy, "Terminaison TLS", "nginx", "Route vers les serveurs applicatifs")
        }
    }

    Deployment_Node(zoneApp, "Zone réseau applicative", "VLAN interne") {
        Deployment_Node(serveurApp, "Serveurs applicatifs x2", "Linux") {
            Container(ihm, "IHM Web", "Java / JSP", "Présentation et saisie")
            Container(service, "Service métier", "Quarkus", "Règles de gestion RH")
        }
        Deployment_Node(serveurBatch, "Serveur de traitements", "Linux") {
            Container(batch, "Batch nocturne", "Java", "Consolidations et exports")
        }
    }

    Deployment_Node(zoneData, "Zone réseau données", "VLAN cloisonné") {
        Deployment_Node(serveurDb, "Serveur de base de données", "Linux") {
            ContainerDb(baseRH, "Base RH", "PostgreSQL", "Dossiers agents et historiques")
        }
    }

    Rel(ihmClient, proxy, "Appelle", "HTTPS 443")
    Rel(proxy, ihm, "Route", "HTTP 8080")
    Rel(service, baseRH, "Lit et écrit", "JDBC/TLS 5432")
    Rel(batch, baseRH, "Lit et écrit", "JDBC/TLS 5432")
```

**Règles** : une **zone réseau par nœud de premier niveau**, protocole et port sur chaque flux,
redondance visible dans le libellé du nœud (`x2`) plutôt que dans une note en marge.

---

## 8 · Niveau code — zone critique

**Type** : UML `classDiagram` · **Portée** : persistance du dossier agent

```mermaid
classDiagram
    class DossierAgentService {
        <<interface>>
        +creer(DossierAgent) Identifiant
        +cloturer(Identifiant, DateCloture) void
    }

    class DossierAgentServiceImpl {
        <<Component>>
        -DossierRepository repository
        -HorlogeSysteme horloge
        +creer(DossierAgent) Identifiant
        +cloturer(Identifiant, DateCloture) void
    }

    class DossierRepository {
        <<interface>>
        +enregistrer(DossierAgent) Identifiant
        +parIdentifiant(Identifiant) DossierAgent
    }

    class DossierRepositoryJdbc {
        <<adapter>>
        -DataSource source
    }

    class DossierAgent {
        -Identifiant id
        -Matricule matricule
        -StatutDossier statut
        +estCloturable() boolean
    }

    DossierAgentService <|.. DossierAgentServiceImpl : implémente
    DossierRepository <|.. DossierRepositoryJdbc : implémente
    DossierAgentServiceImpl --> DossierRepository : dépend de
    DossierAgentServiceImpl --> DossierAgent : manipule
    DossierRepositoryJdbc --> DossierAgent : hydrate
```

**Règles** : ne descendre au niveau code que sur une zone **critique et stable**. Un
`classDiagram` recopiant un package entier est faux au premier refactoring.

---

## Anti-patterns à refuser

| Anti-pattern | Pourquoi c'est un problème |
|---|---|
| Diagramme ASCII | Non maintenable, illisible dès qu'il grossit |
| PNG / JPG / export comme source | La source doit être diffable et modifiable |
| C4 reproduit à la main en `flowchart` | Notation maison que personne ne reconnaît, et deux notations C4 dans un même dépôt |
| Niveaux C4 mélangés | Le lecteur ne sait plus à quelle échelle il regarde |
| Relations sans libellé | Une flèche muette ne dit pas ce qui circule |
| Noms différents entre sections 3, 5, 6, 7 | Le lecteur croit voir deux éléments distincts |
| Couleur porteuse de la seule information | Inaccessible, illisible à l'impression |
| Diagramme de plus d'une quinzaine d'éléments | À fractionner en vues focalisées |
| Technologie affichée partout | Bruit ; ne l'indiquer que là où elle contraint l'architecture |
| Diagramme non mis à jour avec le code | Pire que pas de diagramme : il induit en erreur |

## Vérification avant livraison

- Chaque bloc s'ouvre par ` ```mermaid ` et se ferme correctement.
- Le type de diagramme est en **première ligne** du bloc (`C4Context`, `C4Container`, `C4Component`,
  `C4Deployment`, `sequenceDiagram`, `classDiagram`), suivi d'un `title`.
- Ordre des paramètres respecté : `Container(alias, "Nom", "Technologie", "Responsabilité")` —
  inverser technologie et responsabilité produit un diagramme valide mais faux.
- Chaque `Rel(...)` porte une **action**, et un **protocole** quand il est significatif.
- Les alias sont alphanumériques, uniques, et identiques d'une vue à l'autre.
- Toute frontière ouverte par `{` est refermée par `}`.
- Le type et la portée sont annoncés au-dessus du bloc.
- En cas de doute sur la syntaxe : **simplifier le diagramme**, ne jamais livrer un bloc cassé.
