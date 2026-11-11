# Exemple — corriger les erreurs vues par l'IDE

**Demande** : « Corrige ce qui ne compile plus dans `InvoiceService.java`. »

**Ce que fait Claude avec le serveur JetBrains branché**

1. `get_file_problems` sur le fichier : l'IDE rend les erreurs de compilation et les avertissements
   d'inspection, avec leurs lignes.
2. Claude corrige les erreurs, puis rappelle `get_file_problems` pour vérifier qu'il n'en reste pas.
3. Pour renommer une méthode mal nommée au passage, il passe par la refactorisation de l'IDE, qui
   met à jour tous les appelants, plutôt que par un remplacement textuel.

**Sans le serveur** : Claude doit lancer le build complet pour voir les erreurs, et ne voit pas les
inspections de l'IDE.
