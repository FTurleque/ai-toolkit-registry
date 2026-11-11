# Exemple — mesurer l'impact avant de modifier une méthode

**Demande** : « Je veux changer la signature de `OrderService.cancel`. Qu'est-ce que ça touche ? »

**Ce que fait Claude avec MINOS branché**

1. `minos_index_status` : l'index du dépôt est-il à jour ?
2. `minos_find_symbols` sur `OrderService.cancel`, pour obtenir l'identifiant du symbole.
3. `minos_find_callers` puis `minos_impact` sur ce symbole : appelants directs et transitifs.
4. `minos_related_tests` : les tests à relancer.
5. Il répond avec la liste des appelants, les modules touchés et les tests, en citant la source
   (index MINOS) et en signalant ce que l'index ne couvre pas.

**Sans MINOS** : une recherche textuelle de `cancel(`, qui rate les appels indirects et remonte
les homonymes.
