# Exemple — vérifier une version avant de répondre

**Demande** : « Quelle est la dernière version LTS de Node.js ? »

**Ce que fait Claude avec la règle installée**

1. La question porte sur un fait daté : il appelle `search_web` avec `Node.js LTS release`.
2. Il lit la page officielle trouvée avec `fetch_url` (nodejs.org), pas un agrégateur.
3. Il répond en citant la source et la date de la page.

**Sans la règle** : Claude répond de mémoire, avec une version qui peut être périmée.

**Cas où il ne cherche pas** : « Renomme cette méthode dans le dépôt » — tout est local, la règle
lui dit de ne pas aller sur le Web.
