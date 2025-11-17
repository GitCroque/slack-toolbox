# Pre-Commit Hooks Guide

Ce guide explique comment installer et utiliser les hooks pre-commit pour maintenir la qualité du code.

## Qu'est-ce que Pre-Commit?

Pre-commit est un framework qui permet d'exécuter automatiquement des vérifications sur votre code avant chaque commit Git. Cela garantit que seul du code de qualité est ajouté au dépôt.

## Installation

### 1. Installer pre-commit

Pre-commit est déjà inclus dans `requirements.txt`. Si ce n'est pas déjà fait:

```bash
pip install pre-commit
```

### 2. Installer les hooks Git

Exécutez cette commande dans le répertoire du projet:

```bash
pre-commit install
```

Cela configure Git pour exécuter automatiquement pre-commit avant chaque commit.

### 3. (Optionnel) Installation pour commit-msg

Pour vérifier aussi les messages de commit:

```bash
pre-commit install --hook-type commit-msg
```

## Hooks Configurés

Notre configuration `.pre-commit-config.yaml` inclut:

### 1. Vérifications Générales
- **trailing-whitespace**: Supprime les espaces en fin de ligne
- **end-of-file-fixer**: Assure une ligne vide en fin de fichier
- **check-yaml**: Vérifie la syntaxe YAML
- **check-json**: Vérifie la syntaxe JSON
- **check-added-large-files**: Détecte les fichiers trop volumineux (>1MB)
- **check-merge-conflict**: Détecte les marqueurs de conflit de merge
- **detect-private-key**: Détecte les clés privées exposées

### 2. Formatage Python
- **black**: Formate automatiquement le code Python (127 caractères/ligne)
- **isort**: Trie et organise les imports Python

### 3. Linting Python
- **flake8**: Analyse le code pour détecter les erreurs et problèmes de style
  - Longueur de ligne max: 127
  - Complexité max: 15
  - Ignore certaines erreurs (E203, E501, W503)

### 4. Sécurité
- **bandit**: Scanne le code pour détecter les vulnérabilités de sécurité
  - Configuration dans `.bandit.yml`
  - Analyse `lib/` et `scripts/`
- **safety**: Vérifie les dépendances pour les vulnérabilités connues

### 5. Documentation
- **pydocstyle**: Vérifie les docstrings Python
  - Convention: Google style
- **markdownlint**: Vérifie la qualité des fichiers Markdown

## Utilisation

### Utilisation Automatique

Une fois installé, pre-commit s'exécute automatiquement à chaque `git commit`:

```bash
git add mon_fichier.py
git commit -m "Mon message"
# Les hooks s'exécutent automatiquement
```

### Exécution Manuelle

#### Sur les fichiers modifiés (staged)
```bash
pre-commit run
```

#### Sur tous les fichiers
```bash
pre-commit run --all-files
```

#### Sur un hook spécifique
```bash
pre-commit run black
pre-commit run flake8
pre-commit run bandit
```

#### Sur des fichiers spécifiques
```bash
pre-commit run --files lib/slack_client.py scripts/users/list_users.py
```

## Premier Run

La première fois que vous exécutez pre-commit, il va télécharger et installer tous les hooks. C'est normal et ça ne se produira qu'une seule fois.

```bash
pre-commit run --all-files
```

Cette commande va:
1. Télécharger tous les hooks configurés
2. Les exécuter sur tous les fichiers du projet
3. Corriger automatiquement les problèmes corrigeables (formatage, etc.)
4. Signaler les problèmes qui nécessitent une correction manuelle

## Résolution des Problèmes

### Hook échoue

Si un hook échoue, deux cas de figure:

#### 1. Correction Automatique

Certains hooks (black, isort, trailing-whitespace) corrigent automatiquement:

```bash
$ git commit -m "Update code"
black....................................................................Failed
- hook id: black
- files were modified by this hook

# Les fichiers ont été corrigés automatiquement
# Il suffit de les ajouter et recommiter

$ git add -u
$ git commit -m "Update code"
# Cette fois ça passe!
```

#### 2. Correction Manuelle

D'autres hooks (flake8, bandit) nécessitent une correction manuelle:

```bash
$ git commit -m "Update code"
flake8...................................................................Failed
- hook id: flake8
- exit code: 1

lib/utils.py:42:80: E501 line too long (132 > 127 characters)
lib/utils.py:55:1: E302 expected 2 blank lines, found 1

# Corrigez les problèmes signalés
# Puis recommitez
```

### Contourner Pre-Commit (À éviter!)

Dans des cas exceptionnels, vous pouvez contourner pre-commit:

```bash
git commit --no-verify -m "Emergency fix"
```

⚠️ **Attention**: N'utilisez ceci qu'en cas d'urgence absolue!

## Mise à Jour des Hooks

Pour mettre à jour tous les hooks vers leurs dernières versions:

```bash
pre-commit autoupdate
```

## Configuration Personnalisée

### Modifier les Hooks

Éditez `.pre-commit-config.yaml` pour:
- Ajouter/supprimer des hooks
- Modifier les arguments des hooks
- Changer les versions

Exemple - désactiver un hook:
```yaml
- repo: https://github.com/pycqa/pydocstyle
  rev: 6.3.0
  hooks:
    - id: pydocstyle
      # Commenté = désactivé
      # - id: pydocstyle
```

### Modifier Bandit

Éditez `.bandit.yml` pour:
- Ajouter des exclusions
- Changer le niveau de sévérité
- Ignorer certains tests

### Modifier Markdownlint

Éditez `.markdownlint.yml` pour:
- Changer la longueur max des lignes
- Activer/désactiver des règles

## Intégration CI/CD

Les mêmes vérifications sont exécutées dans notre pipeline CI/CD (GitHub Actions). Donc si pre-commit passe localement, le CI devrait aussi passer!

## Commandes Utiles

```bash
# Installer les hooks
pre-commit install

# Désinstaller les hooks
pre-commit uninstall

# Exécuter sur tous les fichiers
pre-commit run --all-files

# Exécuter un hook spécifique
pre-commit run black --all-files

# Mettre à jour les hooks
pre-commit autoupdate

# Voir les hooks installés
pre-commit run --help

# Nettoyer le cache
pre-commit clean
```

## Bonnes Pratiques

1. **Toujours installer pre-commit** lors du setup d'un nouveau clone:
   ```bash
   git clone <repo>
   cd <repo>
   pip install -r requirements.txt
   pre-commit install
   ```

2. **Exécuter sur tous les fichiers** après modification de config:
   ```bash
   pre-commit run --all-files
   ```

3. **Commit fréquemment**: Plus les commits sont petits, plus c'est facile de corriger les problèmes

4. **Lire les messages d'erreur**: Les hooks donnent des messages clairs sur ce qui doit être corrigé

5. **Ne pas contourner**: Si pre-commit détecte un problème, c'est qu'il y a un problème!

## Aide

Pour plus d'informations:
- Documentation pre-commit: https://pre-commit.com
- Black: https://black.readthedocs.io
- Flake8: https://flake8.pycqa.org
- Bandit: https://bandit.readthedocs.io
- isort: https://pycqa.github.io/isort/

## Troubleshooting

### "command not found: pre-commit"

```bash
pip install pre-commit
# Ou avec le requirements.txt
pip install -r requirements.txt
```

### Hooks trop lents

Les hooks sont exécutés en parallèle quand possible. Si c'est toujours lent:

```bash
# Désactiver certains hooks lourds
# Éditez .pre-commit-config.yaml et commentez les hooks inutiles
```

### Erreurs de syntaxe dans .pre-commit-config.yaml

```bash
# Vérifier la syntaxe YAML
pre-commit validate-config
```

### Cache corrompu

```bash
# Nettoyer et réinstaller
pre-commit clean
pre-commit install --install-hooks
```
