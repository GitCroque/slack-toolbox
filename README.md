# Slack Management Platform

Une collection complète de scripts pour gérer, auditer et administrer votre espace de travail Slack.

> 📚 **Nouveau !** [Guide complet de l'API Slack](SLACK_API_GUIDE.md) - Documentation détaillée pour comprendre et utiliser l'API Slack

## 🎯 Fonctionnalités

### Gestion des Utilisateurs
- 📋 Lister tous les utilisateurs avec détails (statut, rôle, email)
- ➕ Inviter des utilisateurs en masse depuis un fichier CSV
- 🚫 Désactiver/réactiver des utilisateurs
- 📊 Exporter la liste des utilisateurs (CSV, JSON)
- 📈 Statistiques sur les utilisateurs (actifs, invités, bots)
- 🔍 Rechercher des utilisateurs par nom, email ou rôle

### Gestion des Canaux et Groupes
- 📝 Lister tous les canaux (publics, privés)
- ➕ Créer des canaux en masse
- 📦 Archiver/désarchiver des canaux
- 👥 Gérer les membres des canaux (ajouter, retirer)
- 🔄 Convertir des canaux (public ↔ privé)
- 📊 Statistiques sur les canaux (activité, nombre de membres)

### Audit et Conformité
- 📜 Exporter l'historique des messages
- 👁️ Logs d'activité des utilisateurs
- 🔐 Audit des permissions et rôles
- 📥 Rapport sur les fichiers partagés
- ⚠️ Détection d'utilisateurs inactifs
- 📊 Rapports de conformité

### Gestion de l'Espace de Travail
- ⚙️ Configurer les paramètres workspace
- 🎨 Gérer les emojis personnalisés
- 🔗 Gérer les intégrations et apps
- 📢 Gérer les webhooks
- 🔔 Notifications et alertes personnalisées

## 🚀 Installation

### Installation automatique (recommandée)

```bash
# Cloner le repository
git clone https://github.com/GitCroque/slack-script.git
cd slack-script

# Installation automatique
./install.sh
```

Le script install.sh va :
- ✅ Vérifier Python 3.8+
- ✅ Installer les dépendances
- ✅ Créer la configuration
- ✅ Configurer les permissions
- ✅ Tester la connexion

### Installation manuelle

```bash
# Installer les dépendances
pip3 install -r requirements.txt

# Copier le fichier de configuration
cp config/config.example.json config/config.json

# Éditer avec votre token Slack
nano config/config.json

# Tester
make test
```

## 🔑 Configuration

### Obtenir votre token Slack

1. Allez sur https://api.slack.com/apps
2. Créez une nouvelle app ou sélectionnez une app existante
3. Dans "OAuth & Permissions", ajoutez les scopes nécessaires :
   - `users:read` - Lire les informations utilisateurs
   - `users:write` - Gérer les utilisateurs
   - `channels:read` - Lire les informations canaux
   - `channels:write` - Gérer les canaux
   - `channels:manage` - Gérer les canaux (archiver, etc.)
   - `channels:history` - Lire l'historique des messages
   - `groups:read` - Lire les canaux privés
   - `groups:write` - Gérer les canaux privés
   - `admin.users:read` - Admin: lire les utilisateurs
   - `admin.users:write` - Admin: gérer les utilisateurs
   - `admin.conversations:read` - Admin: lire les conversations
   - `admin.conversations:write` - Admin: gérer les conversations
   - `files:read` - Lire les fichiers
   - `emoji:read` - Lire les emojis

4. Installez l'app dans votre workspace
5. Copiez le "Bot User OAuth Token" (commence par `xoxb-`)

### Fichier de configuration

Éditez `config/config.json`:

```json
{
  "slack_token": "xoxb-YOUR-ACTUAL-TOKEN-HERE",
  "workspace_name": "VotreSociete",
  "default_export_format": "csv",
  "timezone": "Europe/Paris"
}
```

## ⚡ Utilisation rapide avec Make

Toutes les commandes sont disponibles via Makefile pour une utilisation simplifiée :

```bash
# Voir toutes les commandes disponibles
make help

# Gestion des utilisateurs
make list-users              # Lister tous les utilisateurs
make list-admins             # Lister les administrateurs
make export-users            # Exporter en CSV
make user-stats              # Statistiques utilisateurs
make invite-users FILE=users.csv  # Inviter depuis CSV

# Gestion des canaux
make list-channels           # Lister tous les canaux
make find-inactive DAYS=90   # Canaux inactifs
make create-channels FILE=channels.csv

# Audit et rapports
make audit-permissions       # Audit des permissions
make inactive-users DAYS=60  # Utilisateurs inactifs
make find-duplicates         # Détecter les doublons
make activity-report DAYS=30 # Rapport d'activité

# Utilitaires
make stats                   # Statistiques workspace
make backup                  # Backup complet
make search QUERY="john"     # Recherche universelle
make dashboard               # Générer dashboard HTML
make validate-csv FILE=users.csv  # Valider CSV
make template TYPE=users     # Générer template CSV

# CLI interactif
make interactive             # Démarrer l'interface interactive
```

## 📚 Guide d'utilisation détaillé

### CLI Interactif

Pour une utilisation simplifiée avec menu interactif :

```bash
make interactive
# ou
python3 slack-manager.py
```

Interface menu avec :
- Gestion des utilisateurs
- Gestion des canaux
- Audit et rapports
- Utilitaires

### Gestion des Utilisateurs

#### Lister tous les utilisateurs
```bash
make list-users
# ou
python3 scripts/users/list_users.py
```

#### Inviter des utilisateurs depuis un CSV
```bash
python3 scripts/users/invite_users.py --file users.csv
```

Format du fichier CSV:
```csv
email,first_name,last_name,channels
user@example.com,John,Doe,"general,random"
```

#### Désactiver un utilisateur
```bash
python3 scripts/users/deactivate_user.py --email user@example.com
```

#### Exporter les utilisateurs
```bash
python3 scripts/users/export_users.py --format csv --output users_export.csv
```

### Gestion des Canaux

#### Lister tous les canaux
```bash
python3 scripts/channels/list_channels.py --include-archived
```

#### Créer des canaux en masse
```bash
python3 scripts/channels/create_channels.py --file channels.csv
```

#### Archiver des canaux inactifs
```bash
python3 scripts/channels/archive_inactive.py --days 90
```

#### Gérer les membres d'un canal
```bash
# Ajouter des membres
python3 scripts/channels/manage_members.py --channel general --add user1@example.com,user2@example.com

# Retirer des membres
python3 scripts/channels/manage_members.py --channel general --remove user@example.com
```

### Audit et Rapports

#### Générer un rapport d'activité
```bash
python3 scripts/audit/activity_report.py --days 30 --output report.pdf
```

#### Exporter l'historique d'un canal
```bash
python3 scripts/audit/export_channel_history.py --channel general --output general_history.json
```

#### Trouver les utilisateurs inactifs
```bash
python3 scripts/audit/inactive_users.py --days 60
```

#### Audit des permissions
```bash
python3 scripts/audit/permissions_audit.py --output permissions_report.csv
```

### Utilitaires

#### Backup complet du workspace
```bash
python3 scripts/utils/full_backup.py --output backup/
```

#### Statistiques globales
```bash
python3 scripts/utils/workspace_stats.py
```

## 📋 Structure du Projet

```
slack-script/
├── README.md
├── requirements.txt
├── config/
│   ├── config.example.json
│   └── config.json (votre configuration)
├── scripts/
│   ├── users/           # Gestion des utilisateurs
│   ├── channels/        # Gestion des canaux
│   ├── audit/           # Audit et conformité
│   ├── workspace/       # Gestion workspace
│   └── utils/           # Utilitaires
├── lib/
│   ├── slack_client.py  # Client Slack centralisé
│   ├── utils.py         # Fonctions utilitaires
│   └── logger.py        # Système de logging
└── examples/
    ├── users.csv
    ├── channels.csv
    └── bulk_operations.md
```

## 🛡️ Sécurité

- **Ne commitez JAMAIS** votre `config/config.json` avec vos tokens
- Le fichier `config/config.json` est dans `.gitignore`
- Utilisez des tokens avec les permissions minimales nécessaires
- Rotez régulièrement vos tokens
- Activez l'audit logging pour toutes les opérations

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer de nouvelles fonctionnalités
- Soumettre des pull requests

## 📄 Licence

MIT License - Voir le fichier LICENSE pour plus de détails

## ⚠️ Avertissement

Ces scripts peuvent effectuer des modifications importantes sur votre workspace Slack. Toujours:
1. Tester sur un workspace de test d'abord
2. Faire des backups avant les opérations de masse
3. Vérifier les permissions de votre token
4. Lire la documentation de chaque script

## 🆕 Nouvelles fonctionnalités

### Makefile - Commandes simplifiées
Utilisation ultra-simplifiée avec `make` :
- `make help` - Liste toutes les commandes
- `make install` - Installation automatique
- `make test` - Test de connexion
- `make stats` - Statistiques rapides
- Plus de 30 commandes disponibles !

### CLI Interactif
Interface menu pour utilisation sans ligne de commande :
```bash
make interactive
```

### Outils avancés
- **Recherche universelle** - Chercher dans users, channels, files
- **Validateur CSV** - Vérifier les CSV avant import
- **Générateur de templates** - Templates CSV prêts à l'emploi
- **Détection de doublons** - Trouver les comptes similaires
- **Rapport d'activité** - Analytics détaillées du workspace
- **Dashboard HTML** - Vue d'ensemble visuelle
- **Gestion emojis** - Lister les emojis personnalisés

### Automatisation
Scripts cron prêts à l'emploi dans `cron/` :
- Backup quotidien automatique
- Rapport hebdomadaire des inactifs
- Audit mensuel complet

Voir `cron/README.md` pour la configuration.

## 🏢 Fonctionnalités Enterprise

### 🧪 Tests Automatisés avec pytest
Suite complète de tests unitaires et d'intégration :
```bash
# Exécuter tous les tests
pytest tests/ -v

# Avec couverture de code
pytest tests/ -v --cov=lib --cov=scripts --cov-report=html

# Tests spécifiques
pytest tests/test_utils.py
pytest tests/test_slack_client.py
```

Configuration dans `pytest.ini` avec fixtures et mocks pour tester sans appels API réels.

### 🔄 CI/CD avec GitHub Actions
Pipeline automatisé à chaque push et pull request :
- ✅ Tests multi-versions Python (3.8, 3.9, 3.10, 3.11)
- ✅ Linting avec flake8 et black
- ✅ Scan de sécurité avec bandit et safety
- ✅ Vérification de build
- ✅ Coverage reporting avec Codecov

Configuration dans `.github/workflows/ci.yml` et `.github/workflows/release.yml`

### 📄 Export PDF des Rapports
Génération de rapports professionnels au format PDF :
```bash
# Export des utilisateurs en PDF
python3 scripts/utils/export_pdf.py --type users --output users.pdf

# Rapport d'audit en PDF
python3 scripts/utils/export_pdf.py --type audit --output audit.pdf

# Rapport d'activité personnalisé
python3 scripts/audit/activity_report.py --days 30 --format pdf --output activity.pdf
```

Rapports formatés avec tableaux, graphiques et mise en page professionnelle.

### 🔔 Notifications Slack via Webhooks
Système de notifications intelligent pour alertes et rapports :
```bash
# Envoyer une notification simple
python3 scripts/utils/send_notification.py --message "Backup terminé avec succès"

# Notification avec formatage riche
python3 scripts/utils/send_notification.py --title "Backup" --message "Terminé" --type success

# Intégration automatique dans les scripts
# - Notifications de backup
# - Alertes de sécurité
# - Rapports d'activité
```

Configurez votre webhook dans `config/config.json` :
```json
{
  "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
}
```

### 🎛️ Assistant de Configuration Interactif
Wizard guidé pour configuration simplifiée :
```bash
python3 setup_wizard.py
```

Le wizard vous guide à travers :
1. ✅ Vérification des prérequis (Python, pip)
2. ✅ Installation des dépendances
3. ✅ Configuration du token Slack (avec aide contextuelle)
4. ✅ Paramètres du workspace
5. ✅ Test de connexion
6. ✅ Configuration optionnelle des webhooks et cron jobs

### 🔍 Comparaison de Backups
Outil pour comparer deux backups et identifier les changements :
```bash
# Comparer deux backups
python3 scripts/utils/compare_backups.py backups/2024-01-01 backups/2024-01-15

# Export en JSON
python3 scripts/utils/compare_backups.py backup1 backup2 --format json --output diff.json

# Export en CSV (fichiers séparés)
python3 scripts/utils/compare_backups.py backup1 backup2 --format csv --output comparison
```

Détecte :
- 👤 Utilisateurs ajoutés/supprimés/modifiés
- 📢 Canaux créés/archivés/modifiés
- 🔐 Changements de permissions
- 📊 Variations de membres par canal
- 📁 Différences de fichiers

### 🚨 Système d'Alertes Intelligent
Détection d'anomalies et alertes automatiques :
```bash
# Scan complet du workspace
python3 scripts/utils/smart_alerts.py

# Avec notifications
python3 scripts/utils/smart_alerts.py --notify

# Comparaison avec snapshot précédent
python3 scripts/utils/smart_alerts.py --compare --notify

# Personnalisation des seuils
python3 scripts/utils/smart_alerts.py --inactive-days 60 --storage-warning 50
```

Détecte automatiquement :
- 👥 **Utilisateurs inactifs** (pourcentage élevé)
- 🔴 **Pics de désactivation** (activité anormale)
- 🔐 **Changements de permissions** (admins/owners)
- 💾 **Usage de stockage** (warnings et critiques)
- 👻 **Comptes invités** (pourcentage élevé)
- 📦 **Archivages massifs** (pics de canaux archivés)
- 🌐 **Partages externes** (canaux partagés)

Niveaux d'alerte : INFO, WARNING, CRITICAL

### 🎣 Pre-commit Hooks
Vérifications automatiques de qualité de code avant chaque commit :
```bash
# Installation
pre-commit install

# Exécuter manuellement
pre-commit run --all-files

# Mise à jour des hooks
pre-commit autoupdate
```

Hooks configurés :
- ✅ **Black** - Formatage automatique du code
- ✅ **isort** - Organisation des imports
- ✅ **Flake8** - Linting et détection d'erreurs
- ✅ **Bandit** - Scan de sécurité
- ✅ **Safety** - Vérification des dépendances
- ✅ **Pydocstyle** - Vérification des docstrings
- ✅ **Markdownlint** - Qualité des fichiers Markdown
- ✅ **Détection de clés privées** et secrets
- ✅ **Validation YAML/JSON**

Voir [PRE_COMMIT_GUIDE.md](PRE_COMMIT_GUIDE.md) pour le guide complet.

## 📖 Documentation

- **[SLACK_API_GUIDE.md](SLACK_API_GUIDE.md)** - Guide complet de l'API Slack (1300+ lignes)
  - Concepts fondamentaux
  - Authentification et permissions
  - Toutes les méthodes API
  - 3 exemples pratiques complets
  - Gestion des erreurs et rate limiting
  - Debugging

- **[PRE_COMMIT_GUIDE.md](PRE_COMMIT_GUIDE.md)** - Guide complet des pre-commit hooks
  - Installation et configuration
  - Utilisation et bonnes pratiques
  - Résolution des problèmes
  - Personnalisation des hooks

- **[FAQ.md](FAQ.md)** - Questions fréquentes et troubleshooting
- **[QUICKSTART.md](QUICKSTART.md)** - Démarrage rapide en 5 minutes
- **[EXAMPLES.md](examples/EXAMPLES.md)** - 30+ exemples d'utilisation
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Guide de contribution

## 🆘 Support

Pour toute question ou problème:
- Ouvrez une issue sur GitHub
- Consultez le [Guide API Slack](SLACK_API_GUIDE.md) pour les détails techniques
- Documentation officielle Slack API: https://api.slack.com/

## 🎯 Roadmap

### ✅ Récemment Implémenté
- [x] Tests automatisés avec pytest
- [x] CI/CD avec GitHub Actions
- [x] Export PDF des rapports
- [x] Notifications Slack via webhooks
- [x] Assistant de configuration interactif
- [x] Comparaison de backups
- [x] Système d'alertes intelligent
- [x] Pre-commit hooks pour qualité de code

### 🚧 En Cours / À Venir
- [ ] Interface web pour gestion simplifiée
- [ ] Support des workspaces multiples
- [ ] Notifications par email (en plus des webhooks)
- [ ] Intégration avec d'autres outils (Google Workspace, etc.)
- [ ] Dashboard analytics en temps réel (actuellement statique)
- [ ] Automatisation avec scheduler intégré (actuellement via cron)
