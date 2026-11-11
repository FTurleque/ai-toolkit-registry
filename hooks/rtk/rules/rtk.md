# Sortie des commandes

La sortie des commandes est ici condensée pour économiser des jetons : chaque signal est gardé, le
bruit coûteux est retiré. Traite-la comme le résultat complet : lance les commandes normalement, et
regroupe les commandes liées en un seul appel pour éviter des tours inutiles.

Une sortie tronquée indique elle-même comment récupérer le reste. Ne relance une commande sous la
forme `rtk proxy <commande>` que si son résultat est inutilisable : vide alors qu'une sortie était
attendue, en contradiction avec son code de retour, ou illisible.
