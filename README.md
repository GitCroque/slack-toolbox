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

### Prérequis
- Python 3.8 ou supérieur
- Un compte Slack avec une offre payante
- Permissions administrateur sur votre workspace Slack

### Installation sur macOS

```bash
# Cloner le repository
git clone https://github.com/GitCroque/slack-script.git
cd slack-script

# Installer les dépendances
pip3 install -r requirements.txt

# Copier le fichier de configuration exemple
cp config/config.example.json config/config.json

# Éditer la configuration avec votre token Slack
nano config/config.json
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

## 📚 Guide d'utilisation

### Gestion des Utilisateurs

#### Lister tous les utilisateurs
```bash
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

## 📖 Documentation

- **[SLACK_API_GUIDE.md](SLACK_API_GUIDE.md)** - Guide complet de l'API Slack (900+ lignes)
  - Concepts fondamentaux
  - Authentification et permissions
  - Toutes les méthodes API
  - Exemples pratiques
  - Gestion des erreurs et rate limiting
  - Debugging

- **[QUICKSTART.md](QUICKSTART.md)** - Démarrage rapide en 5 minutes
- **[EXAMPLES.md](examples/EXAMPLES.md)** - 30+ exemples d'utilisation
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Guide de contribution

## 🆘 Support

Pour toute question ou problème:
- Ouvrez une issue sur GitHub
- Consultez le [Guide API Slack](SLACK_API_GUIDE.md) pour les détails techniques
- Documentation officielle Slack API: https://api.slack.com/

## 🎯 Roadmap

- [ ] Interface web pour gestion simplifiée
- [ ] Support des workspaces multiples
- [ ] Notifications par email
- [ ] Intégration avec d'autres outils (Google Workspace, etc.)
- [ ] Dashboard analytics en temps réel
- [ ] Automatisation avec scheduler intégré
