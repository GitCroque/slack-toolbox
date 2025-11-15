# Guide de contribution

Merci de votre intérêt pour contribuer à Slack Management Platform ! 🎉

## Comment contribuer

### Signaler un bug

1. Vérifiez que le bug n'a pas déjà été signalé dans les [Issues](https://github.com/GitCroque/slack-script/issues)
2. Créez une nouvelle issue avec :
   - Un titre descriptif
   - Les étapes pour reproduire le bug
   - Le comportement attendu vs obtenu
   - Votre environnement (macOS version, Python version)
   - Les logs d'erreur si disponibles

### Proposer une fonctionnalité

1. Ouvrez une issue avec le tag "enhancement"
2. Décrivez la fonctionnalité et son utilité
3. Discutez de l'implémentation avec la communauté

### Soumettre du code

1. **Fork** le repository
2. Créez une **branche** pour votre fonctionnalité :
   ```bash
   git checkout -b feature/ma-nouvelle-fonctionnalite
   ```
3. Développez votre fonctionnalité
4. Testez votre code
5. Commitez avec des messages clairs :
   ```bash
   git commit -m "Add: nouvelle fonctionnalité X"
   ```
6. Poussez vers votre fork :
   ```bash
   git push origin feature/ma-nouvelle-fonctionnalite
   ```
7. Ouvrez une **Pull Request**

## Standards de code

### Python

- Suivre PEP 8 pour le style de code
- Utiliser des docstrings pour les fonctions
- Ajouter des commentaires pour la logique complexe
- Gérer les erreurs avec try/except appropriés

Exemple :

```python
def ma_fonction(param1: str, param2: int) -> bool:
    """
    Description courte de la fonction

    Args:
        param1: Description du paramètre 1
        param2: Description du paramètre 2

    Returns:
        Description du retour
    """
    try:
        # Code ici
        return True
    except Exception as e:
        logger.error(f"Erreur: {e}")
        return False
```

### Structure des scripts

Tous les scripts doivent :

1. Commencer par le shebang `#!/usr/bin/env python3`
2. Avoir une docstring décrivant leur fonction
3. Importer les modules système, puis les modules du projet
4. Utiliser argparse pour les arguments CLI
5. Avoir une fonction `main()` et `if __name__ == '__main__':`
6. Utiliser le logger pour les messages
7. Gérer les erreurs et retourner des codes d'erreur appropriés

### Messages de commit

Format recommandé :

```
Type: Description courte (max 50 caractères)

Description plus détaillée si nécessaire.
Expliquer POURQUOI ce changement est fait.

Fixes #123
```

Types :
- `Add:` - Nouvelle fonctionnalité
- `Fix:` - Correction de bug
- `Update:` - Amélioration d'une fonctionnalité existante
- `Refactor:` - Refactorisation du code
- `Docs:` - Documentation uniquement
- `Test:` - Ajout de tests
- `Chore:` - Maintenance (dépendances, etc.)

## Tests

Avant de soumettre une PR :

1. Testez votre code manuellement
2. Vérifiez qu'il n'y a pas de régression
3. Testez avec `--dry-run` si applicable
4. Vérifiez que tous les scripts existants fonctionnent encore

## Documentation

Toute nouvelle fonctionnalité doit inclure :

1. Docstrings dans le code
2. Mise à jour du README.md si nécessaire
3. Exemple d'utilisation dans examples/EXAMPLES.md
4. Commentaires dans le code pour la logique complexe

## Idées de contributions

### Scripts à ajouter

- Gestion des emojis personnalisés
- Gestion des webhooks
- Statistiques avancées avec graphiques
- Export vers d'autres formats (Excel, PDF)
- Interface web/GUI
- Notifications automatiques
- Intégration avec d'autres outils (Google Workspace, etc.)

### Améliorations

- Tests unitaires
- CI/CD (GitHub Actions)
- Support pour workspaces multiples
- Gestion asynchrone pour meilleures performances
- Internationalisation (i18n)
- Mode interactif (TUI)

## Questions ?

N'hésitez pas à :
- Ouvrir une issue pour poser des questions
- Commenter sur les issues/PRs existantes
- Contacter les mainteneurs

## Code de conduite

- Soyez respectueux et professionnel
- Acceptez les critiques constructives
- Focalisez-vous sur ce qui est meilleur pour le projet
- Aidez les nouveaux contributeurs

Merci de contribuer ! 🙏
