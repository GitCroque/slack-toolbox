# Architecture de la Plateforme de Gestion Slack

## Vue d'ensemble

La Plateforme de Gestion Slack est une suite d'outils en ligne de commande conçue pour gérer, auditer et administrer les espaces de travail Slack de manière professionnelle et sécurisée.

### Principes de conception

1. **Modularité** - Chaque composant a une responsabilité unique et bien définie
2. **Réutilisabilité** - Code partagé dans `lib/`, scripts spécialisés dans `scripts/`
3. **Sécurité** - Validation des entrées, gestion sécurisée des tokens, audit trail
4. **Extensibilité** - Architecture permettant l'ajout facile de nouvelles fonctionnalités
5. **Testabilité** - Code testable avec mocks pour éviter les appels API réels

## Structure du projet

```
slack-script/
├── lib/                          # Bibliothèque principale
│   ├── slack_client.py          # Client API Slack (wrapper)
│   ├── utils.py                 # Utilitaires généraux
│   ├── logger.py                # Configuration logging
│   ├── validators.py            # Validation des entrées
│   ├── script_base.py           # Classe de base pour scripts
│   ├── alerts.py                # Système d'alertes
│   ├── notifier.py              # Système de notifications
│   └── pdf_generator.py         # Génération de PDF
│
├── scripts/                      # Scripts CLI organisés par domaine
│   ├── users/                   # Gestion des utilisateurs
│   ├── channels/                # Gestion des canaux
│   ├── audit/                   # Audit et conformité
│   ├── workspace/               # Configuration workspace
│   ├── backup/                  # Sauvegarde et restauration
│   ├── reports/                 # Rapports et analytics
│   ├── monitoring/              # Surveillance et alertes
│   └── tools/                   # Outils utilitaires
│
├── tests/                        # Tests unitaires et d'intégration
├── config/                       # Configuration
├── cron/                         # Scripts d'automatisation
├── examples/                     # Exemples et templates
├── .github/workflows/            # CI/CD GitHub Actions
└── docs/                         # Documentation (guides, FAQ, etc.)
```

## Composants principaux

### 1. Bibliothèque Core (`lib/`)

#### SlackManager (`slack_client.py`)
- **Responsabilité** : Wrapper autour de slack-sdk pour centraliser les appels API
- **Fonctionnalités** :
  - Gestion de l'authentification
  - Méthodes haut niveau pour opérations courantes
  - Gestion centralisée des erreurs
  - Rate limiting et retry logic

```python
class SlackManager:
    def __init__(self, config_path=None)
    def list_users() -> List[Dict]
    def list_channels() -> List[Dict]
    def create_channel(name, is_private=False) -> Dict
    # ... autres méthodes
```

#### Utilities (`utils.py`)
- **Responsabilité** : Fonctions utilitaires réutilisables
- **Fonctionnalités** :
  - Manipulation CSV/JSON (save_to_csv, load_csv, etc.)
  - Formatage (format_timestamp, format_bytes, etc.)
  - Affichage (print_table, progress_bar, etc.)
  - Helpers (sanitize_channel_name, confirm_action, etc.)

#### Validators (`validators.py`)
- **Responsabilité** : Validation et sanitization des entrées
- **Fonctionnalités** :
  - Validation d'emails, noms de canaux, IDs
  - Validation de chemins de fichiers (anti path-traversal)
  - Validation de formats (dates, URLs, etc.)
  - Exceptions personnalisées (ValidationError)

#### Script Base (`script_base.py`)
- **Responsabilité** : Classe de base pour réduire le boilerplate
- **Fonctionnalités** :
  - Parsing d'arguments standardisé
  - Initialisation logger et client Slack
  - Gestion d'erreurs cohérente
  - Lifecycle management (setup, execute, cleanup)
  - Support du dry-run mode

```python
class SlackScript:
    def __init__(name, description, require_slack=True)
    def setup_arguments(parser)      # Override pour args personnalisés
    def execute()                     # Override pour logique principale
    def run()                         # Méthode principale
```

#### Alert System (`alerts.py`)
- **Responsabilité** : Détection d'anomalies et alertes intelligentes
- **Fonctionnalités** :
  - Détection d'utilisateurs inactifs
  - Détection de pics de désactivation
  - Surveillance des changements de permissions
  - Alertes de stockage
  - Niveaux de sévérité (INFO, WARNING, CRITICAL)

#### Notifier (`notifier.py`)
- **Responsabilité** : Envoi de notifications multi-canal
- **Fonctionnalités** :
  - Webhooks Slack
  - Email (optionnel)
  - Multi-notifier pour envoi parallèle
  - Formatage riche des messages

#### PDF Generator (`pdf_generator.py`)
- **Responsabilité** : Génération de rapports PDF
- **Fonctionnalités** :
  - Mise en page professionnelle
  - Tables formatées
  - En-têtes et pieds de page
  - Graphiques basiques

### 2. Scripts CLI (`scripts/`)

#### Organisation par domaine

##### Users (`scripts/users/`)
- `list_users.py` - Lister tous les utilisateurs
- `invite_users.py` - Invitation en masse
- `deactivate_user.py` - Désactivation d'utilisateurs
- `export_users.py` - Export CSV/JSON
- `user_stats.py` - Statistiques utilisateurs

##### Channels (`scripts/channels/`)
- `list_channels.py` - Lister tous les canaux
- `create_channels.py` - Création en masse
- `archive_channel.py` - Archivage
- `manage_members.py` - Gestion des membres
- `find_inactive.py` - Trouver canaux inactifs

##### Audit (`scripts/audit/`)
- `permissions_audit.py` - Audit des permissions
- `inactive_users.py` - Détection d'inactifs
- `export_channel_history.py` - Export historique
- `file_report.py` - Rapport sur les fichiers
- `activity_report.py` - Rapport d'activité
- `find_duplicates.py` - Détection de doublons

##### Backup (`scripts/backup/`)
- `create_backup.py` - Créer une sauvegarde complète
- `compare_backups.py` - Comparer deux sauvegardes

##### Reports (`scripts/reports/`)
- `export_pdf.py` - Export PDF des rapports
- `generate_dashboard.py` - Dashboard HTML
- `workspace_stats.py` - Statistiques workspace

##### Monitoring (`scripts/monitoring/`)
- `smart_alerts.py` - Système d'alertes intelligent
- `send_notification.py` - Envoi de notifications

##### Tools (`scripts/tools/`)
- `search.py` - Recherche universelle
- `validate_csv.py` - Validation de CSV
- `generate_template.py` - Génération de templates
- `test_connection.py` - Test de connexion

### 3. Tests (`tests/`)

#### Structure des tests
```
tests/
├── conftest.py              # Fixtures pytest
├── test_slack_client.py     # Tests du client Slack
├── test_utils.py            # Tests des utilitaires
├── test_validators.py       # Tests de validation
├── test_csv_validation.py   # Tests validation CSV
└── test_integration.py      # Tests d'intégration
```

#### Stratégie de test
- **Unit tests** : Chaque fonction isolée avec mocks
- **Integration tests** : Workflows complets end-to-end
- **Mocking** : slack-sdk est mocké pour éviter appels API réels
- **Coverage** : Objectif 80%+

### 4. CI/CD (`.github/workflows/`)

#### Workflows

**CI Pipeline** (`ci.yml`)
1. Tests multi-versions Python (3.8, 3.9, 3.10, 3.11)
2. Linting (flake8, black)
3. Security scanning (bandit, safety)
4. Tests avec coverage
5. Upload coverage à Codecov

**Release Pipeline** (`release.yml`)
1. Déclenché sur tags version (v*)
2. Build du package
3. Création de release GitHub automatique

## Flux de données

### 1. Authentification et Configuration

```
User → config/config.json → SlackManager → slack-sdk → Slack API
```

1. L'utilisateur configure son token dans `config/config.json`
2. SlackManager charge la configuration au démarrage
3. slack-sdk utilise le token pour les appels API
4. Toutes les réponses passent par SlackManager pour traitement

### 2. Exécution d'un script

```
CLI → SlackScript.run() → setup → execute → cleanup
```

1. **Parsing** : Arguments parsés via argparse
2. **Setup** : Logger initialisé, config chargée, Slack client créé
3. **Validation** : Arguments validés
4. **Execute** : Logique principale du script
5. **Cleanup** : Ressources libérées (toujours exécuté)

### 3. Gestion des erreurs

```
Exception → Logger → User (console + fichier)
                  → Cleanup (toujours exécuté)
```

1. Exceptions spécifiques utilisées (SlackApiError, ValidationError, etc.)
2. Erreurs loggées avec contexte
3. Cleanup toujours exécuté (finally block)
4. Exit code approprié retourné (0=succès, 1=erreur, 130=interrompu)

### 4. Système d'alertes

```
Workspace Data → AlertDetector → Alerts → AlertManager → Notifications
```

1. **Collection** : Données workspace collectées (users, channels, files)
2. **Detection** : Alertes détectées par AlertDetector
3. **Management** : Alertes stockées et filtrées par AlertManager
4. **Notification** : Envoi via Notifier (Slack/Email)

## Patterns et conventions

### 1. Naming Conventions

- **Fichiers** : `snake_case.py`
- **Classes** : `PascalCase`
- **Fonctions/Méthodes** : `snake_case()`
- **Constantes** : `UPPER_SNAKE_CASE`
- **Variables privées** : `_leading_underscore`

### 2. Docstrings

Format Google style :

```python
def function_name(param1: str, param2: int = 0) -> bool:
    """
    Brief description of function.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 0)

    Returns:
        Description of return value

    Raises:
        ValueError: Description of when this is raised

    Example:
        >>> function_name('test', 5)
        True
    """
```

### 3. Error Handling

```python
# ✅ GOOD - Exceptions spécifiques
try:
    result = slack.api_call()
except SlackApiError as e:
    logger.error(f"API error: {e}")
except ValidationError as e:
    logger.error(f"Validation error: {e}")

# ❌ BAD - Exception générique
try:
    result = slack.api_call()
except Exception as e:
    logger.error(f"Error: {e}")
```

### 4. Logging

```python
# Niveaux appropriés
logger.debug("Detailed information for debugging")
logger.info("General information about progress")
logger.warning("Warning about potential issues")
logger.error("Error that caused operation to fail")
logger.critical("Critical error requiring immediate attention")
```

### 5. Type Hints

```python
from typing import List, Dict, Optional, Union

def process_users(
    users: List[Dict[str, Any]],
    filter_role: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Process users with optional filtering."""
    pass
```

## Sécurité

### 1. Token Management

- ✅ Token stocké dans `config/config.json` (gitignored)
- ✅ Pas de token hardcodé dans le code
- ✅ Validation du format du token
- ✅ Config example sans token réel

### 2. Input Validation

- ✅ Tous les inputs validés via `validators.py`
- ✅ Protection contre path traversal
- ✅ Validation des emails, IDs Slack, URLs
- ✅ Sanitization des noms de canaux

### 3. API Security

- ✅ Principe du moindre privilège (scopes minimaux)
- ✅ Rate limiting respecté
- ✅ Retry logic avec backoff exponentiel
- ✅ Timeouts configurés

### 4. Logging Security

- ✅ Webhook URLs sanitisées dans les logs
- ✅ Tokens jamais loggés
- ✅ Audit log pour opérations sensibles
- ✅ Permissions fichiers de log appropriées

## Performance

### 1. Pagination

```python
# API Slack limite à 200 résultats par page
def list_all_users():
    all_users = []
    cursor = None

    while True:
        response = client.users_list(cursor=cursor, limit=200)
        all_users.extend(response['members'])

        cursor = response.get('response_metadata', {}).get('next_cursor')
        if not cursor:
            break

    return all_users
```

### 2. Rate Limiting

- Respect des limites Slack (Tier 3 : ~50+ requêtes/minute)
- Backoff exponentiel en cas d'erreur 429
- Batch processing avec délais configurables

### 3. Caching

- Résultats de certaines requêtes cachés temporairement
- Cache invalidé après modifications
- TTL configurables

## Évolutivité

### Ajouter un nouveau script

1. Créer le fichier dans le répertoire approprié (`scripts/<domain>/`)
2. Hériter de `SlackScript` pour réduire le boilerplate
3. Implémenter `execute()` avec la logique métier
4. Ajouter les tests dans `tests/`
5. Ajouter la commande dans `Makefile`
6. Mettre à jour la documentation

### Ajouter une nouvelle fonctionnalité lib

1. Ajouter le code dans `lib/<module>.py`
2. Exporter via `lib/__init__.py`
3. Ajouter les type hints
4. Documenter avec docstrings
5. Ajouter les tests
6. Mettre à jour ARCHITECTURE.md si nécessaire

## Dépendances

### Production

- `slack-sdk` : Client officiel Slack API
- `requests` : HTTP client pour webhooks
- `reportlab` : Génération de PDF (optionnel)
- `pypdf` : Manipulation de PDF (optionnel)

### Development

- `pytest` : Framework de test
- `pytest-cov` : Coverage de code
- `pytest-mock` : Mocking pour tests
- `black` : Formatage de code
- `isort` : Organisation des imports
- `flake8` : Linting
- `bandit` : Security scanning
- `mypy` : Type checking
- `pre-commit` : Git hooks

## Déploiement

### Installation standard

```bash
# Cloner le repo
git clone https://github.com/GitCroque/slack-script.git
cd slack-script

# Installation en mode éditable
pip install -e .

# Configuration
cp config/config.example.json config/config.json
# Éditer config/config.json avec votre token

# Test
slack-test
```

### Installation pour développement

```bash
# Installation avec dépendances dev
pip install -e ".[dev]"

# Installer pre-commit hooks
pre-commit install

# Lancer les tests
pytest tests/ -v --cov
```

## Maintenance

### Mise à jour des dépendances

```bash
# Mettre à jour requirements.txt
pip-compile requirements.in

# Vérifier les vulnérabilités
safety check
```

### Monitoring

- CI/CD GitHub Actions pour chaque commit
- Coverage automatique sur Codecov
- Security scanning avec bandit et safety
- Pre-commit hooks pour qualité de code

## Ressources

- **Repository** : https://github.com/GitCroque/slack-script
- **Documentation Slack API** : https://api.slack.com/
- **Issues** : https://github.com/GitCroque/slack-script/issues
