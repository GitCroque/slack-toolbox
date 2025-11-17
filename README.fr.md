# 🚀 Plateforme de Gestion Slack - Documentation Française

> **Suite d'outils professionnels pour la gestion d'espaces de travail Slack**
>
> Gérez vos utilisateurs, canaux, audits et sauvegardes avec des outils en ligne de commande puissants

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-213%20passent-success)](./tests/)

---

## 📋 Table des Matières

- [Fonctionnalités](#-fonctionnalités)
- [Installation Rapide](#-installation-rapide)
- [Configuration](#️-configuration)
- [Utilisation](#-utilisation)
- [Commandes Principales](#-commandes-principales)
- [Sécurité](#-sécurité)
- [Documentation Complète](#-documentation-complète)

---

## ✨ Fonctionnalités

### 👥 Gestion des Utilisateurs
- ✅ Lister tous les utilisateurs avec filtres (rôle, statut)
- ✅ Inviter des utilisateurs en masse depuis CSV
- ✅ Exporter les données utilisateurs (CSV/JSON)
- ✅ Désactiver des utilisateurs
- ✅ Statistiques détaillées des utilisateurs
- ✅ Détecter les utilisateurs inactifs

### 💬 Gestion des Canaux
- ✅ Lister tous les canaux (publics/privés)
- ✅ Créer des canaux en masse depuis CSV
- ✅ Archiver des canaux inactifs
- ✅ Gérer les membres des canaux
- ✅ Détecter les canaux sans activité

### 🔍 Audit et Conformité
- ✅ Audit des permissions et rôles
- ✅ Rapports d'activité détaillés
- ✅ Détection d'utilisateurs dupliqués
- ✅ Historique des canaux
- ✅ Rapports sur les fichiers partagés

### 💾 Sauvegarde et Récupération
- ✅ Sauvegarde complète de l'espace de travail
- ✅ Comparaison de sauvegardes
- ✅ Export des historiques de messages
- ✅ Sauvegarde incrémentielle

### 📊 Rapports et Monitoring
- ✅ Statistiques de l'espace de travail
- ✅ Tableaux de bord personnalisables
- ✅ Export PDF des rapports
- ✅ Alertes intelligentes (détection d'anomalies)
- ✅ Notifications multi-canaux (Slack, Email)

### 🛠️ Outils Utilitaires
- ✅ Test de connexion Slack
- ✅ Validation de fichiers CSV
- ✅ Génération de templates
- ✅ Recherche avancée

---

## 🚀 Installation Rapide

### Option 1 : Installation Automatique (Recommandé)

```bash
# Cloner le dépôt
git clone https://github.com/GitCroque/slack-toolbox.git
cd slack-toolbox

# Lancer l'assistant de configuration
python3 setup_wizard.py
```

L'assistant va :
1. ✅ Installer les dépendances Python
2. ✅ Créer la configuration
3. ✅ Tester la connexion Slack
4. ✅ Configurer les hooks git (optionnel)

### Option 2 : Installation Manuelle

```bash
# Installer les dépendances
pip install -r requirements.txt

# Copier la configuration
cp config/config.example.json config/config.json

# Éditer avec votre token Slack
nano config/config.json
```

### Option 3 : Installation via pip (Package)

```bash
pip install slack-management-platform
```

---

## ⚙️ Configuration

### 1. Obtenir un Token Slack

1. Visitez https://api.slack.com/apps
2. Créez une nouvelle application ou sélectionnez-en une existante
3. Naviguez vers "OAuth & Permissions"
4. Ajoutez les scopes OAuth nécessaires :
   - `users:read` - Lire les informations utilisateurs
   - `channels:read` - Lire les canaux
   - `channels:write` - Créer/modifier des canaux
   - `users:write` - Inviter des utilisateurs
   - `admin.users:read` - Lire les infos admin
   - `admin.users:write` - Gérer les utilisateurs (admin)

5. Installez l'app dans votre espace de travail
6. Copiez le **Bot User OAuth Token** (commence par `xoxb-`)

### 2. Configuration du Token

Éditez `config/config.json` :

```json
{
  "slack_token": "xoxb-votre-token-ici",
  "max_retries": 3,
  "rate_limit_delay": 1,
  "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
}
```

### 3. Test de Connexion

```bash
python scripts/tools/test_connection.py
```

Vous devriez voir :
```
✅ Connecté à l'espace de travail Slack: VotreEntreprise
   Utilisateur bot: @votre-bot
```

---

## 💻 Utilisation

### Interface CLI Interactive

```bash
python slack-manager.py
```

Menu interactif avec toutes les fonctionnalités :
```
=== Gestionnaire Slack ===
1. Gestion des utilisateurs
2. Gestion des canaux
3. Audit et rapports
4. Sauvegardes
5. Outils
6. Quitter
```

### Commandes Directes (Makefile)

Le projet inclut un Makefile avec 60+ commandes :

```bash
# Afficher l'aide
make help

# Gestion des utilisateurs
make list-users              # Lister tous les utilisateurs
make invite-users            # Inviter depuis CSV
make export-users            # Exporter les utilisateurs

# Gestion des canaux
make list-channels           # Lister tous les canaux
make create-channels         # Créer depuis CSV
make find-inactive-channels  # Trouver les canaux inactifs

# Audit
make audit-permissions       # Auditer les permissions
make activity-report         # Rapport d'activité
make find-duplicates         # Détecter les doublons

# Sauvegarde
make backup                  # Sauvegarde complète
make compare-backups         # Comparer les sauvegardes

# Monitoring
make smart-alerts            # Alertes intelligentes
make workspace-stats         # Statistiques de l'espace

# Test
make test                    # Exécuter les tests
make test-connection         # Tester la connexion
```

---

## 🎯 Commandes Principales

### Lister les Utilisateurs

```bash
# Tous les utilisateurs actifs
python scripts/users/list_users.py

# Avec filtres
python scripts/users/list_users.py --role admin
python scripts/users/list_users.py --include-deleted
python scripts/users/list_users.py --include-bots

# Export
python scripts/users/list_users.py --export csv --output users.csv
python scripts/users/list_users.py --export json --output users.json
```

### Inviter des Utilisateurs

```bash
# Depuis un fichier CSV
python scripts/users/invite_users.py examples/users_template.csv

# Mode dry-run (test sans modifications)
python scripts/users/invite_users.py examples/users_template.csv --dry-run
```

Format CSV :
```csv
email,first_name,last_name,channels
john@example.com,John,Doe,general;random
jane@example.com,Jane,Smith,general
```

### Créer des Canaux

```bash
# Depuis un fichier CSV
python scripts/channels/create_channels.py examples/channels_template.csv

# Avec preview
python scripts/channels/create_channels.py channels.csv --dry-run
```

### Audit de Permissions

```bash
# Audit complet
python scripts/audit/permissions_audit.py

# Export en CSV
python scripts/audit/permissions_audit.py --output audit_results.csv
```

### Sauvegarde Complète

```bash
# Sauvegarde de l'espace de travail
make backup

# Ou directement
python scripts/backup/create_backup.py
```

### Alertes Intelligentes

```bash
# Détection d'anomalies
python scripts/monitoring/smart_alerts.py --config config/alerts.json
```

---

## 🔐 Sécurité

### Bonnes Pratiques

1. **Protection du Token**
   - ⚠️ **JAMAIS** commiter `config/config.json` dans git
   - Utilisez `.gitignore` (déjà configuré)
   - Stockez le token dans un gestionnaire de secrets en production

2. **Permissions Minimales**
   - N'accordez que les scopes OAuth nécessaires
   - Utilisez des tokens avec durée de vie limitée
   - Auditez régulièrement les permissions

3. **Validation des Entrées**
   - Toutes les entrées sont validées
   - Protection contre path traversal
   - Validation des emails, noms de canaux, etc.

4. **Logs Sécurisés**
   - Les tokens ne sont jamais loggés
   - Logs stockés dans `logs/` (gitignored)
   - Rotation automatique des logs

5. **Mode Dry-Run**
   - Testez toujours avec `--dry-run` d'abord
   - Vérifiez les changements avant application
   - Aucune modification avec dry-run actif

### Sécurité CI/CD

Le projet inclut :
- ✅ Scan de sécurité avec Bandit
- ✅ Vérification des dépendances avec Safety
- ✅ Pre-commit hooks pour éviter les commits de secrets
- ✅ Vérification automatique des fichiers sensibles

---

## 📚 Documentation Complète

### Documentation Technique

- **[README.md](./README.md)** - Documentation complète (EN)
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Architecture détaillée
- **[QUICKSTART.md](./QUICKSTART.md)** - Guide de démarrage rapide
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** - Guide de contribution
- **[FAQ.md](./FAQ.md)** - Questions fréquentes
- **[SLACK_API_GUIDE.md](./SLACK_API_GUIDE.md)** - Guide API Slack
- **[PRE_COMMIT_GUIDE.md](./PRE_COMMIT_GUIDE.md)** - Guide des hooks

### Exemples et Templates

Tous les templates sont dans `examples/` :
- `users_template.csv` - Template pour inviter des utilisateurs
- `channels_template.csv` - Template pour créer des canaux
- `alerts_config.json` - Configuration des alertes
- `backup_config.json` - Configuration des sauvegardes

### Tests

```bash
# Exécuter tous les tests
make test

# Tests avec couverture
make test-coverage

# Tests d'un module spécifique
pytest tests/test_validators.py -v
```

**Statistiques des tests** :
- ✅ 213 tests passent
- ✅ Couverture : ~45%+
- ✅ Tests unitaires, d'intégration et de scripts

---

## 🛠️ Développement

### Installation Environnement de Développement

```bash
# Cloner et installer
git clone https://github.com/GitCroque/slack-toolbox.git
cd slack-toolbox

# Installer avec dépendances de dev
pip install -e ".[dev,test]"

# Installer les pre-commit hooks
pre-commit install
```

### Structure du Projet

```
slack-toolbox/
├── lib/                    # Bibliothèque core
│   ├── slack_client.py    # Client API Slack
│   ├── script_base.py     # Classe de base pour scripts
│   ├── validators.py      # Validation des entrées
│   ├── utils.py           # Fonctions utilitaires
│   ├── alerts.py          # Système d'alertes
│   ├── notifier.py        # Notifications
│   └── pdf_generator.py   # Génération PDF
├── scripts/               # Scripts CLI
│   ├── users/            # Gestion utilisateurs
│   ├── channels/         # Gestion canaux
│   ├── audit/            # Audit et conformité
│   ├── backup/           # Sauvegardes
│   ├── monitoring/       # Monitoring
│   ├── reports/          # Rapports
│   ├── tools/            # Outils
│   └── workspace/        # Config espace
├── tests/                # Suite de tests
├── config/               # Configuration
├── examples/             # Templates et exemples
├── cron/                 # Scripts automation
└── docs/                 # Documentation
```

### Qualité du Code

Le projet maintient des standards élevés :
- **Linting** : flake8, black, isort
- **Type checking** : mypy (strict mode)
- **Sécurité** : bandit, safety
- **Tests** : pytest, 213 tests
- **Documentation** : Docstrings Google-style
- **CI/CD** : GitHub Actions (Python 3.8-3.11)

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Consultez [CONTRIBUTING.md](./CONTRIBUTING.md) pour :
- Guidelines de contribution
- Standards de code
- Processus de review
- Workflow git

### Quick Start Contribution

```bash
# Fork et clone
git clone https://github.com/VOUS/slack-toolbox.git

# Créer une branche
git checkout -b feature/ma-fonctionnalite

# Faire vos changements
# ...

# Tests et quality checks
make test
make lint

# Commit et push
git add .
git commit -m "Add: Ma nouvelle fonctionnalité"
git push origin feature/ma-fonctionnalite

# Créer une Pull Request
```

---

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- [Slack SDK for Python](https://github.com/slackapi/python-slack-sdk) - Client officiel Slack
- [ReportLab](https://www.reportlab.com/) - Génération PDF
- Tous les contributeurs qui ont aidé à améliorer ce projet

---

## 📞 Support

- **Issues** : https://github.com/GitCroque/slack-toolbox/issues
- **Documentation** : Voir les fichiers `*.md` dans le dépôt
- **Email** : gitcroque@example.com

---

**⭐ Si ce projet vous aide, n'hésitez pas à lui donner une étoile sur GitHub !**
