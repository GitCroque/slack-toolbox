# 🛠️ Guide de Développement - Slack Management Platform

> Guide complet pour les développeurs souhaitant contribuer au projet Slack Management Platform

## 📋 Table des matières

- [Setup Environnement de Développement](#-setup-environnement-de-développement)
- [Standards de Code](#-standards-de-code)
- [Tests et Couverture](#-tests-et-couverture)
- [Pre-commit Hooks](#-pre-commit-hooks)
- [CI/CD Workflow](#-cicd-workflow)
- [Guide de Contribution](#-guide-de-contribution)
- [Architecture du Code](#-architecture-du-code)
- [Ajouter de Nouvelles Fonctionnalités](#-ajouter-de-nouvelles-fonctionnalités)

---

## 🚀 Setup Environnement de Développement

### Prérequis

- **Python** : 3.8 ou supérieur (testé sur 3.8, 3.9, 3.10, 3.11)
- **Git** : Pour le versioning
- **pip** : Gestionnaire de paquets Python
- **virtualenv** ou **venv** : Pour l'isolation de l'environnement

### Installation de l'environnement

#### 1. Cloner le repository

```bash
# Cloner le projet
git clone https://github.com/GitCroque/slack-script.git
cd slack-script

# Vérifier la branche principale
git checkout main
```

#### 2. Créer et activer un environnement virtuel

```bash
# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement (Linux/macOS)
source venv/bin/activate

# Activer l'environnement (Windows)
venv\Scripts\activate

# Vérifier l'activation
which python  # Devrait pointer vers venv/bin/python
```

#### 3. Installer les dépendances de développement

```bash
# Installer toutes les dépendances (production + développement + tests)
pip install --upgrade pip
pip install -r requirements.txt

# Ou installer via pyproject.toml avec toutes les options
pip install -e ".[all]"

# Installer uniquement les dépendances de développement
pip install -e ".[dev,test]"
```

#### 4. Configuration initiale

```bash
# Copier le fichier de configuration exemple
cp config/config.example.json config/config.json

# Éditer avec votre token Slack (pour les tests locaux)
nano config/config.json
```

#### 5. Installer les pre-commit hooks

```bash
# Installer pre-commit
pip install pre-commit

# Installer les hooks dans le projet
pre-commit install

# Vérifier l'installation
pre-commit --version
```

#### 6. Vérifier l'installation

```bash
# Tester l'importation des modules
python -c "from lib.slack_client import SlackManager; print('✅ OK')"
python -c "from lib.utils import load_config; print('✅ OK')"

# Lancer la suite de tests
pytest tests/ -v
```

### Configuration de l'IDE

#### Visual Studio Code

Créer `.vscode/settings.json` :

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length=127"],
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests/"]
}
```

#### PyCharm

1. **Interpreter** : File → Settings → Project → Python Interpreter → Add → Existing Environment → `venv/bin/python`
2. **Code Style** : Settings → Editor → Code Style → Python → Set from → Predefined Style → Black
3. **Tests** : Settings → Tools → Python Integrated Tools → Testing → Default test runner : pytest

---

## 📏 Standards de Code

Le projet utilise des outils d'analyse statique pour maintenir une qualité de code élevée et une cohérence dans toute la codebase.

### Black - Formatage du code

**Black** est le formateur de code officiel du projet. Il assure une cohérence automatique du style.

#### Configuration (pyproject.toml)

```toml
[tool.black]
line-length = 127
target-version = ['py38', 'py39', 'py310', 'py311']
include = '\.pyi?$'
```

#### Utilisation

```bash
# Formater tous les fichiers Python
black lib/ scripts/ tests/

# Vérifier sans modifier (mode dry-run)
black --check lib/ scripts/

# Formater un fichier spécifique
black lib/slack_client.py

# Voir les différences qui seraient appliquées
black --diff lib/
```

#### Via Makefile

```bash
make format
```

### isort - Tri des imports

**isort** organise automatiquement les imports Python dans l'ordre standard.

#### Configuration (pyproject.toml)

```toml
[tool.isort]
profile = "black"
line_length = 127
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
```

#### Utilisation

```bash
# Trier les imports de tous les fichiers
isort lib/ scripts/ tests/

# Vérifier sans modifier
isort --check-only lib/

# Voir les différences
isort --diff lib/slack_client.py

# Trier un fichier spécifique
isort lib/slack_client.py
```

#### Ordre des imports

```python
# 1. Imports de la bibliothèque standard
import os
import sys
from typing import Dict, List, Optional

# 2. Imports de bibliothèques tierces
import requests
from slack_sdk import WebClient

# 3. Imports locaux
from lib.utils import load_config
from lib.logger import setup_logger
```

### flake8 - Linting et analyse de code

**flake8** vérifie la conformité PEP 8 et détecte les erreurs potentielles.

#### Configuration (.pre-commit-config.yaml)

```yaml
args: [
  '--max-line-length=127',
  '--extend-ignore=E203,E501,W503',
  '--exclude=.git,__pycache__,venv,env,.venv',
  '--max-complexity=15'
]
```

#### Utilisation

```bash
# Analyser tout le projet
flake8 lib/ scripts/ tests/

# Analyser avec statistiques
flake8 lib/ scripts/ --statistics

# Ignorer certains warnings
flake8 lib/ --extend-ignore=E402,F401

# Analyser un fichier spécifique
flake8 lib/slack_client.py
```

#### Codes d'erreur courants

- **E203** : Whitespace before ':' (désactivé pour compatibilité Black)
- **E501** : Line too long (géré par Black)
- **F401** : Module imported but unused
- **F821** : Undefined name
- **W503** : Line break before binary operator (style préféré)

### mypy - Vérification de types statiques

**mypy** assure la cohérence des annotations de types Python.

#### Configuration (pyproject.toml)

```toml
[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
strict_equality = true
show_error_codes = true
ignore_missing_imports = true
```

#### Utilisation

```bash
# Vérifier tous les fichiers
mypy lib/ scripts/

# Vérifier un fichier spécifique
mypy lib/slack_client.py

# Afficher les erreurs avec plus de détails
mypy --show-error-codes lib/

# Ignorer les imports manquants
mypy --ignore-missing-imports lib/
```

#### Exemple d'annotations de types

```python
from typing import Dict, List, Optional, Any

def get_users(
    client: WebClient,
    limit: int = 100,
    include_deleted: bool = False
) -> List[Dict[str, Any]]:
    """
    Récupère la liste des utilisateurs.

    Args:
        client: Client Slack SDK
        limit: Nombre maximum d'utilisateurs
        include_deleted: Inclure les utilisateurs désactivés

    Returns:
        Liste de dictionnaires contenant les données utilisateurs
    """
    users: List[Dict[str, Any]] = []
    # ... implémentation
    return users
```

### Outils complémentaires

#### bandit - Analyse de sécurité

```bash
# Scanner le projet pour des vulnérabilités
bandit -r lib/ scripts/

# Scanner avec rapport JSON
bandit -r lib/ scripts/ -f json -o bandit-report.json

# Ignorer certains tests
bandit -r lib/ --skip B101,B601
```

#### pylint - Linting avancé

```bash
# Analyser avec pylint (plus strict que flake8)
pylint lib/ scripts/

# Générer un rapport
pylint lib/ --output-format=text > pylint-report.txt

# Désactiver certains warnings
pylint lib/ --disable=C0111,R0903
```

#### pydocstyle - Vérification des docstrings

```bash
# Vérifier les docstrings (convention Google)
pydocstyle lib/ scripts/ --convention=google
```

---

## 🧪 Tests et Couverture

Le projet utilise **pytest** pour les tests unitaires et d'intégration, avec une couverture de code suivie par **coverage.py**.

### Structure des tests

```
tests/
├── conftest.py              # Fixtures globales et configuration
├── test_slack_client.py     # Tests du client Slack
├── test_utils.py            # Tests des utilitaires
├── test_validators.py       # Tests des validateurs
├── test_script_base.py      # Tests de la classe de base
├── test_all_scripts.py      # Tests de tous les scripts
├── test_integration.py      # Tests d'intégration
└── test_csv_validation.py   # Tests de validation CSV
```

### Configuration pytest

#### pyproject.toml

```toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers --cov=lib --cov=scripts"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

### Lancer les tests

#### Tests basiques

```bash
# Lancer tous les tests
pytest

# Mode verbose avec détails
pytest -v

# Tests spécifiques
pytest tests/test_slack_client.py

# Tester une fonction spécifique
pytest tests/test_utils.py::test_load_config

# Arrêter au premier échec
pytest -x

# Lancer les tests en parallèle (nécessite pytest-xdist)
pytest -n auto
```

#### Tests avec couverture

```bash
# Tests avec rapport de couverture
pytest --cov=lib --cov=scripts

# Rapport détaillé dans le terminal
pytest --cov=lib --cov=scripts --cov-report=term-missing

# Générer un rapport HTML
pytest --cov=lib --cov=scripts --cov-report=html
open htmlcov/index.html  # Ouvrir le rapport

# Générer un rapport XML (pour CI/CD)
pytest --cov=lib --cov=scripts --cov-report=xml

# Via Makefile
make test-coverage
```

### Fixtures pytest

#### Fixtures globales (conftest.py)

```python
import pytest
from unittest.mock import Mock, MagicMock

@pytest.fixture
def mock_slack_client():
    """Mock du client Slack SDK."""
    client = Mock()
    client.users_list.return_value = {
        "ok": True,
        "members": [
            {"id": "U123", "name": "john", "real_name": "John Doe"}
        ]
    }
    return client

@pytest.fixture
def sample_config():
    """Configuration de test."""
    return {
        "slack_token": "xoxb-test-token",
        "workspace_name": "test-workspace"
    }

@pytest.fixture
def temp_config_file(tmp_path):
    """Fichier de configuration temporaire."""
    config_file = tmp_path / "config.json"
    config_file.write_text('{"slack_token": "test"}')
    return str(config_file)
```

#### Utilisation des fixtures

```python
def test_load_config(temp_config_file):
    """Test de chargement de configuration."""
    from lib.utils import load_config

    config = load_config(temp_config_file)
    assert config["slack_token"] == "test"

def test_get_users(mock_slack_client):
    """Test de récupération des utilisateurs."""
    from lib.slack_client import SlackManager

    manager = SlackManager(mock_slack_client)
    users = manager.get_users()

    assert len(users) == 1
    assert users[0]["name"] == "john"
```

### Tests avec mocks

```python
from unittest.mock import Mock, patch, MagicMock

def test_with_mock():
    """Test avec mock simple."""
    mock_client = Mock()
    mock_client.users_list.return_value = {"ok": True, "members": []}

    # Utiliser le mock
    result = mock_client.users_list()
    assert result["ok"] is True

@patch('lib.slack_client.WebClient')
def test_with_patch(mock_webclient):
    """Test avec patch."""
    mock_instance = mock_webclient.return_value
    mock_instance.auth_test.return_value = {"ok": True}

    # Le WebClient est maintenant mocké
    from lib.slack_client import SlackManager
    manager = SlackManager("fake-token")

    assert manager.test_connection() is True
```

### Tests paramétrés

```python
import pytest

@pytest.mark.parametrize("email,expected", [
    ("user@example.com", True),
    ("invalid-email", False),
    ("user@", False),
    ("@example.com", False),
])
def test_validate_email(email, expected):
    """Test de validation d'email avec plusieurs cas."""
    from lib.validators import is_valid_email

    assert is_valid_email(email) == expected
```

### Couverture de code

#### Configuration (pyproject.toml)

```toml
[tool.coverage.run]
source = ["lib", "scripts"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__pycache__/*",
    "*/venv/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@(abc\\.)?abstractmethod",
]
```

#### Objectifs de couverture

- **Minimum acceptable** : 80%
- **Objectif** : 90%
- **Fichiers critiques** (lib/) : 95%+

---

## 🎣 Pre-commit Hooks

Les **pre-commit hooks** s'exécutent automatiquement avant chaque commit pour garantir la qualité du code.

### Installation

```bash
# Installer pre-commit
pip install pre-commit

# Installer les hooks dans le repository
pre-commit install

# Vérifier l'installation
pre-commit --version
```

### Configuration

Le fichier `.pre-commit-config.yaml` définit tous les hooks :

```yaml
repos:
  # Vérifications de fichiers générales
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: detect-private-key

  # Formatage avec Black
  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
        args: ['--line-length=127']

  # Tri des imports avec isort
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ['--profile=black', '--line-length=127']

  # Linting avec flake8
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=127', '--extend-ignore=E203,E501,W503']

  # Analyse de sécurité avec bandit
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.6
    hooks:
      - id: bandit
        args: ['-c', '.bandit.yml', '-r', 'lib/', 'scripts/']

  # Vérification des docstrings
  - repo: https://github.com/pycqa/pydocstyle
    rev: 6.3.0
    hooks:
      - id: pydocstyle
        args: ['--convention=google']
```

### Utilisation

```bash
# Les hooks s'exécutent automatiquement à chaque commit
git commit -m "Mon commit"

# Lancer manuellement les hooks sur tous les fichiers
pre-commit run --all-files

# Lancer un hook spécifique
pre-commit run black --all-files
pre-commit run flake8 --all-files

# Mettre à jour les hooks vers les dernières versions
pre-commit autoupdate

# Contourner les hooks (à éviter !)
git commit --no-verify -m "Commit sans hooks"
```

### Via Makefile

```bash
# Installer les hooks
make pre-commit-install

# Lancer les hooks
make pre-commit-run

# Mettre à jour les hooks
make pre-commit-update
```

### Workflow typique

```bash
# 1. Faire des modifications
nano lib/slack_client.py

# 2. Ajouter les fichiers
git add lib/slack_client.py

# 3. Commiter (les hooks s'exécutent automatiquement)
git commit -m "Add: nouvelle méthode get_user_by_email"
# ✅ Pre-commit exécute : black, isort, flake8, bandit, etc.

# 4. Si les hooks modifient des fichiers (black, isort)
git add lib/slack_client.py  # Re-ajouter les fichiers modifiés
git commit -m "Add: nouvelle méthode get_user_by_email"
```

---

## 🔄 CI/CD Workflow

Le projet utilise **GitHub Actions** pour l'intégration et le déploiement continus.

### Architecture du pipeline

Le pipeline CI/CD est défini dans `.github/workflows/ci.yml` et comprend 4 jobs principaux :

1. **test** : Exécution des tests sur plusieurs versions de Python
2. **lint** : Vérification de la qualité du code
3. **security** : Scan de sécurité
4. **build** : Vérification de build et tests d'intégration

### Job : Tests

```yaml
test:
  runs-on: ubuntu-latest
  strategy:
    matrix:
      python-version: ['3.8', '3.9', '3.10', '3.11']
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
    - run: pip install -r requirements.txt
    - run: pytest tests/ -v --cov=lib --cov=scripts --cov-report=xml
    - uses: codecov/codecov-action@v3
```

**Ce qui est testé** :
- Compatibilité multi-versions Python (3.8 à 3.11)
- Suite de tests complète avec pytest
- Couverture de code (envoyée à Codecov)

### Job : Linting

```yaml
lint:
  runs-on: ubuntu-latest
  steps:
    - run: pip install flake8 black pylint
    - run: flake8 lib/ scripts/ --max-line-length=127
    - run: black --check lib/ scripts/
```

**Ce qui est vérifié** :
- Conformité PEP 8 avec flake8
- Formatage du code avec black
- Analyse statique avec pylint

### Job : Sécurité

```yaml
security:
  runs-on: ubuntu-latest
  steps:
    - run: pip install bandit safety
    - run: bandit -r lib/ scripts/
    - run: safety check --json
```

**Ce qui est scanné** :
- Vulnérabilités de code avec bandit
- Vulnérabilités de dépendances avec safety

### Déclencheurs du pipeline

```yaml
on:
  push:
    branches: [ main, claude/* ]
  pull_request:
    branches: [ main ]
```

Le pipeline se déclenche sur :
- **Push** sur `main` ou branches `claude/*`
- **Pull Request** vers `main`

### Badges de statut

Ajouter dans le README.md :

```markdown
![CI Status](https://github.com/GitCroque/slack-script/workflows/CI%2FCD%20Pipeline/badge.svg)
![Coverage](https://codecov.io/gh/GitCroque/slack-script/branch/main/graph/badge.svg)
```

---

## 🤝 Guide de Contribution

### Workflow Git

#### 1. Fork et clone

```bash
# Fork le projet sur GitHub, puis cloner votre fork
git clone https://github.com/VOTRE-USERNAME/slack-script.git
cd slack-script

# Ajouter le repository upstream
git remote add upstream https://github.com/GitCroque/slack-script.git

# Vérifier les remotes
git remote -v
```

#### 2. Créer une branche

```bash
# Mettre à jour main
git checkout main
git pull upstream main

# Créer une branche pour votre fonctionnalité
git checkout -b feature/nom-de-la-fonctionnalite

# Ou pour un bugfix
git checkout -b fix/nom-du-bug

# Ou pour de la documentation
git checkout -b docs/sujet-documentation
```

**Convention de nommage des branches** :
- `feature/` : Nouvelles fonctionnalités
- `fix/` : Corrections de bugs
- `docs/` : Documentation
- `refactor/` : Refactoring
- `test/` : Ajout de tests
- `chore/` : Maintenance

#### 3. Développer et commiter

```bash
# Faire vos modifications
nano lib/slack_client.py

# Vérifier les changements
git status
git diff

# Ajouter les fichiers
git add lib/slack_client.py

# Commiter avec un message descriptif
git commit -m "Add: méthode get_user_by_email dans SlackManager"
```

### Convention de commits

Format : `<type>: <description>`

**Types de commits** :
- `Add:` Nouvelle fonctionnalité
- `Fix:` Correction de bug
- `Update:` Mise à jour de fonctionnalité existante
- `Remove:` Suppression de code
- `Refactor:` Refactoring sans changement de fonctionnalité
- `Docs:` Documentation uniquement
- `Test:` Ajout ou modification de tests
- `Style:` Formatage, pas de changement de logique
- `Chore:` Maintenance, dépendances, configuration

**Exemples** :

```bash
git commit -m "Add: support de filtrage par département dans list_users"
git commit -m "Fix: correction du bug de pagination dans get_all_channels"
git commit -m "Update: amélioration des performances de export_users"
git commit -m "Docs: ajout de la doc pour la fonction validate_email"
git commit -m "Test: ajout des tests unitaires pour SlackManager"
git commit -m "Refactor: extraction de la logique de retry dans utils"
```

#### 4. Pousser et créer une Pull Request

```bash
# Pousser la branche vers votre fork
git push origin feature/nom-de-la-fonctionnalite

# Créer une Pull Request sur GitHub
# Aller sur https://github.com/GitCroque/slack-script et cliquer "New Pull Request"
```

### Template de Pull Request

```markdown
## 📝 Description

Brève description des changements apportés.

## 🎯 Type de changement

- [ ] 🐛 Bugfix
- [ ] ✨ Nouvelle fonctionnalité
- [ ] 📝 Documentation
- [ ] ♻️  Refactoring
- [ ] ✅ Tests

## 🧪 Tests

- [ ] Tests unitaires ajoutés/mis à jour
- [ ] Tests d'intégration ajoutés/mis à jour
- [ ] Tous les tests passent localement
- [ ] Couverture de code maintenue/améliorée

## ✅ Checklist

- [ ] Code formaté avec Black
- [ ] Imports triés avec isort
- [ ] Aucun warning flake8
- [ ] Docstrings ajoutées/mises à jour
- [ ] Pre-commit hooks passent
- [ ] Documentation mise à jour si nécessaire

## 📸 Captures d'écran (si applicable)

## 📚 Documentation liée

Issues fermées : #123, #456
```

### Processus de review

1. **Automatique** : CI/CD vérifie tests, linting, sécurité
2. **Code Review** : Un mainteneur examine le code
3. **Discussion** : Échanges sur les changements proposés
4. **Corrections** : Application des retours si nécessaire
5. **Merge** : Fusion dans `main` après approbation

---

## 🏗️ Architecture du Code

### Vue d'ensemble

```
slack-script/
├── lib/                    # Bibliothèque core réutilisable
│   ├── slack_client.py     # Client Slack API (SlackManager)
│   ├── utils.py            # Utilitaires généraux
│   ├── validators.py       # Validation des entrées
│   ├── logger.py           # Configuration des logs
│   ├── script_base.py      # Classe de base pour scripts
│   ├── alerts.py           # Système d'alertes intelligentes
│   ├── notifier.py         # Notifications Slack
│   └── pdf_generator.py    # Génération de rapports PDF
│
├── scripts/                # Scripts CLI organisés par domaine
│   ├── users/              # Gestion utilisateurs
│   ├── channels/           # Gestion canaux
│   ├── audit/              # Audit et conformité
│   ├── workspace/          # Configuration workspace
│   ├── utils/              # Outils utilitaires
│   └── ...
```

### Composants principaux

#### SlackManager (lib/slack_client.py)

Classe principale pour interagir avec l'API Slack.

```python
from lib.slack_client import SlackManager

# Initialisation
manager = SlackManager(token="xoxb-your-token")

# Méthodes principales
users = manager.get_users()
channels = manager.get_channels()
user = manager.get_user_by_id("U123ABC")
```

#### ScriptBase (lib/script_base.py)

Classe de base pour tous les scripts, fournit des fonctionnalités communes.

```python
from lib.script_base import ScriptBase

class MyScript(ScriptBase):
    def run(self):
        self.logger.info("Démarrage du script")
        # Logique du script
        self.logger.info("Terminé")
```

#### Validators (lib/validators.py)

Fonctions de validation pour les entrées utilisateur.

```python
from lib.validators import is_valid_email, validate_csv

if is_valid_email("user@example.com"):
    # Email valide
    pass
```

### Principes de conception

1. **Séparation des responsabilités** : Chaque module a un rôle précis
2. **DRY (Don't Repeat Yourself)** : Code réutilisable dans `lib/`
3. **Single Responsibility** : Une classe/fonction = une responsabilité
4. **Testabilité** : Code facilement testable avec mocks
5. **Documentation** : Docstrings pour toutes les fonctions publiques

---

## ➕ Ajouter de Nouvelles Fonctionnalités

### Créer un nouveau script

#### 1. Choisir la catégorie

```bash
# Gestion utilisateurs
scripts/users/

# Gestion canaux
scripts/channels/

# Audit et rapports
scripts/audit/

# Utilitaires
scripts/utils/
```

#### 2. Créer le fichier

```bash
# Exemple : nouveau script pour exporter les utilisateurs en XML
touch scripts/users/export_users_xml.py
chmod +x scripts/users/export_users_xml.py
```

#### 3. Template de base

```python
#!/usr/bin/env python3
"""
Export users to XML format.

Ce script exporte tous les utilisateurs du workspace au format XML.
"""

import argparse
import sys
from typing import List, Dict, Any

from lib.script_base import ScriptBase
from lib.slack_client import SlackManager
from lib.utils import save_xml


class ExportUsersXML(ScriptBase):
    """Script pour exporter les utilisateurs en XML."""

    def __init__(self, output_file: str = "users.xml"):
        """
        Initialise le script.

        Args:
            output_file: Chemin du fichier de sortie XML
        """
        super().__init__()
        self.output_file = output_file

    def run(self) -> None:
        """Exécute le script d'export."""
        self.logger.info("Démarrage de l'export XML des utilisateurs")

        # Récupérer les utilisateurs
        users = self.slack_manager.get_users()
        self.logger.info(f"Trouvé {len(users)} utilisateurs")

        # Convertir en XML
        xml_data = self._convert_to_xml(users)

        # Sauvegarder
        save_xml(xml_data, self.output_file)
        self.logger.info(f"✅ Export terminé : {self.output_file}")

    def _convert_to_xml(self, users: List[Dict[str, Any]]) -> str:
        """Convertit les utilisateurs en XML."""
        # Implémentation de la conversion
        pass


def main() -> int:
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="Export users to XML format"
    )
    parser.add_argument(
        "-o", "--output",
        default="users.xml",
        help="Output XML file"
    )

    args = parser.parse_args()

    try:
        script = ExportUsersXML(output_file=args.output)
        script.run()
        return 0
    except Exception as e:
        print(f"❌ Erreur : {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

#### 4. Ajouter les tests

```bash
# Créer le fichier de test
touch tests/test_export_users_xml.py
```

```python
"""Tests pour export_users_xml."""

import pytest
from unittest.mock import Mock, patch

from scripts.users.export_users_xml import ExportUsersXML


def test_export_users_xml(mock_slack_client, tmp_path):
    """Test de l'export XML."""
    output_file = tmp_path / "users.xml"

    script = ExportUsersXML(output_file=str(output_file))
    script.run()

    assert output_file.exists()
    content = output_file.read_text()
    assert "<users>" in content
```

#### 5. Mettre à jour la documentation

```bash
# Ajouter dans README.md
nano README.md
```

#### 6. Tester

```bash
# Tests unitaires
pytest tests/test_export_users_xml.py -v

# Test manuel
python scripts/users/export_users_xml.py --output test.xml
```

### Ajouter une nouvelle fonctionnalité à la bibliothèque

#### 1. Modifier lib/slack_client.py

```python
def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
    """
    Récupère un utilisateur par son email.

    Args:
        email: Adresse email de l'utilisateur

    Returns:
        Dictionnaire utilisateur ou None si non trouvé
    """
    try:
        response = self.client.users_lookupByEmail(email=email)
        if response["ok"]:
            return response["user"]
        return None
    except Exception as e:
        self.logger.error(f"Erreur recherche utilisateur : {e}")
        return None
```

#### 2. Ajouter les tests

```python
def test_get_user_by_email(mock_slack_client):
    """Test de recherche par email."""
    from lib.slack_client import SlackManager

    manager = SlackManager(mock_slack_client)
    user = manager.get_user_by_email("john@example.com")

    assert user is not None
    assert user["name"] == "john"
```

### Checklist avant soumission

- [ ] Code fonctionne et testé manuellement
- [ ] Tests unitaires écrits et passent
- [ ] Couverture de code maintenue (> 80%)
- [ ] Code formaté avec Black
- [ ] Imports triés avec isort
- [ ] Aucun warning flake8
- [ ] Aucune erreur mypy
- [ ] Docstrings complètes (Google style)
- [ ] Pre-commit hooks passent
- [ ] Documentation mise à jour
- [ ] Exemple d'utilisation ajouté

---

## 📚 Ressources

- **Documentation Slack API** : https://api.slack.com/
- **Python Style Guide (PEP 8)** : https://pep8.org/
- **pytest Documentation** : https://docs.pytest.org/
- **Black Documentation** : https://black.readthedocs.io/
- **mypy Documentation** : https://mypy.readthedocs.io/
- **pre-commit** : https://pre-commit.com/

---

## 💬 Support

- **Issues** : https://github.com/GitCroque/slack-script/issues
- **Discussions** : https://github.com/GitCroque/slack-script/discussions
- **Email** : gitcroque@example.com

---

**Dernière mise à jour** : 2025-11-17
