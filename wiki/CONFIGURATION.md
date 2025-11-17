# ⚙️ Guide de Configuration

Guide complet pour configurer Slack Toolbox.

---

## 📋 Obtenir un Token Slack

### Étape 1 : Créer une Application Slack

1. Visitez https://api.slack.com/apps
2. Cliquez sur **"Create New App"**
3. Choisissez **"From scratch"**
4. Donnez un nom (ex: "Workspace Manager")
5. Sélectionnez votre espace de travail

### Étape 2 : Configurer les Permissions (Scopes)

Dans **"OAuth & Permissions"**, ajoutez ces **Bot Token Scopes** :

#### Permissions Utilisateurs
- `users:read` - Lire les informations utilisateurs
- `users:read.email` - Lire les emails
- `admin.users:read` - Admin: lire les utilisateurs
- `admin.users:write` - Admin: gérer les utilisateurs

#### Permissions Canaux
- `channels:read` - Lire les canaux publics
- `channels:write` - Gérer les canaux publics
- `channels:manage` - Gérer (archiver, etc.)
- `channels:history` - Lire l'historique
- `groups:read` - Lire les canaux privés
- `groups:write` - Gérer les canaux privés
- `groups:history` - Historique privé

#### Permissions Fichiers
- `files:read` - Lire les fichiers

#### Permissions Workspace
- `team:read` - Infos du workspace
- `emoji:read` - Emojis personnalisés

### Étape 3 : Installer l'Application

1. Dans **"OAuth & Permissions"**
2. Cliquez **"Install to Workspace"**
3. Autorisez l'application
4. **Copiez le "Bot User OAuth Token"** (commence par `xoxb-`)

---

## 🔧 Configuration du Fichier

### Configuration de Base

```bash
# Copier le template
cp config/config.example.json config/config.json

# Éditer
nano config/config.json
```

### Structure du Fichier

```json
{
  "slack_token": "xoxb-votre-token-ici",
  "workspace_name": "VotreEntreprise",
  "max_retries": 3,
  "rate_limit_delay": 1,
  "default_export_format": "csv",
  "timezone": "Europe/Paris",
  "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
  "log_level": "INFO"
}
```

### Paramètres Détaillés

| Paramètre | Type | Obligatoire | Description |
|-----------|------|-------------|-------------|
| `slack_token` | string | ✅ Oui | Token d'application Slack (xoxb-...) |
| `workspace_name` | string | ❌ Non | Nom de votre espace (pour logs) |
| `max_retries` | int | ❌ Non | Nombre de tentatives (défaut: 3) |
| `rate_limit_delay` | float | ❌ Non | Délai entre appels API (défaut: 1s) |
| `default_export_format` | string | ❌ Non | Format export par défaut (csv/json) |
| `timezone` | string | ❌ Non | Fuseau horaire (défaut: UTC) |
| `webhook_url` | string | ❌ Non | URL webhook pour notifications |
| `log_level` | string | ❌ Non | Niveau de log (DEBUG/INFO/WARNING/ERROR) |

---

## 🔔 Configuration des Alertes

### Fichier alerts.json

Créez `config/alerts.json` pour configurer les alertes :

```json
{
  "enabled": true,
  "checks": {
    "inactive_users": {
      "enabled": true,
      "threshold_days": 90,
      "severity": "WARNING"
    },
    "permission_changes": {
      "enabled": true,
      "severity": "CRITICAL"
    },
    "storage_usage": {
      "enabled": true,
      "threshold_percent": 80,
      "severity": "WARNING"
    },
    "new_admins": {
      "enabled": true,
      "severity": "INFO"
    }
  },
  "notification": {
    "webhook": true,
    "email": false
  }
}
```

### Types d'Alertes

| Type | Description | Sévérité Par Défaut |
|------|-------------|---------------------|
| `inactive_users` | Utilisateurs inactifs depuis X jours | WARNING |
| `permission_changes` | Changements de permissions admin | CRITICAL |
| `storage_usage` | Stockage au-dessus du seuil | WARNING |
| `new_admins` | Nouveaux administrateurs | INFO |
| `deleted_users` | Utilisateurs supprimés | INFO |
| `new_guests` | Nouveaux invités | INFO |

---

## 📧 Configuration des Notifications

### Webhook Slack

```json
{
  "webhook_url": "https://hooks.slack.com/services/T00/B00/xxx"
}
```

Pour obtenir un webhook :
1. Visitez https://api.slack.com/apps
2. Sélectionnez votre app
3. "Incoming Webhooks" → Activer
4. "Add New Webhook to Workspace"
5. Choisir un canal
6. Copier l'URL

### Email (optionnel)

```json
{
  "email": {
    "enabled": true,
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_user": "votre@email.com",
    "smtp_password": "votre-mot-de-passe-app",
    "from_address": "slack-alerts@votreentreprise.com",
    "to_addresses": ["admin@votreentreprise.com"]
  }
}
```

**Note** : Pour Gmail, créez un "App Password" dans vos paramètres de sécurité.

---

## 💾 Configuration des Sauvegardes

### Fichier backup.json

```json
{
  "backup_dir": "./backups",
  "include": {
    "users": true,
    "channels": true,
    "messages": false,
    "files": false
  },
  "retention_days": 90,
  "compression": true,
  "encryption": false
}
```

### Options de Sauvegarde

| Option | Description | Défaut |
|--------|-------------|--------|
| `backup_dir` | Répertoire des sauvegardes | `./backups` |
| `users` | Inclure les utilisateurs | `true` |
| `channels` | Inclure les canaux | `true` |
| `messages` | Inclure les messages (volumineux) | `false` |
| `files` | Inclure les fichiers (très volumineux) | `false` |
| `retention_days` | Jours de rétention | `90` |
| `compression` | Compresser (gzip) | `true` |
| `encryption` | Chiffrer (nécessite clé) | `false` |

---

## 🔐 Sécurité de la Configuration

### Protection du Token

**✅ À FAIRE** :
- Ajouter `config/config.json` au `.gitignore` (déjà fait)
- Ne JAMAIS commiter le fichier de config
- Utiliser des variables d'environnement en production
- Rotation régulière des tokens

**❌ À NE PAS FAIRE** :
- Partager votre token
- Commiter le config dans git
- Utiliser le même token partout
- Laisser le token en clair sur un serveur partagé

### Variables d'Environnement

Alternative sécurisée au fichier config :

```bash
export SLACK_TOKEN="xoxb-votre-token"
export SLACK_WEBHOOK="https://hooks.slack.com/..."
```

Puis dans le code :
```python
import os
token = os.getenv('SLACK_TOKEN')
```

### Fichier .env

Créez `.env` (gitignored) :

```bash
SLACK_TOKEN=xoxb-votre-token
SLACK_WEBHOOK=https://hooks.slack.com/...
MAX_RETRIES=3
```

Chargez avec python-dotenv :
```bash
pip install python-dotenv
```

---

## 🧪 Test de la Configuration

### Test Rapide

```bash
python scripts/tools/test_connection.py
```

Sortie attendue :
```
✅ Connecté à l'espace de travail Slack: VotreEntreprise
   Utilisateur bot: @votre-bot
   Team ID: T1234567890
```

### Test Complet

```bash
# Tester les permissions utilisateurs
python scripts/users/list_users.py --dry-run

# Tester les permissions canaux
python scripts/channels/list_channels.py --dry-run

# Tester les notifications
python scripts/monitoring/send_notification.py --test
```

### Vérifier les Permissions

```bash
make audit-permissions
```

Affiche toutes vos permissions actuelles et manquantes.

---

## 🔄 Configuration Avancée

### Plusieurs Espaces de Travail

Créez plusieurs fichiers de config :

```bash
config/
├── production.json
├── staging.json
└── dev.json
```

Utilisez avec :
```bash
python script.py --config config/production.json
```

### Configuration par Environnement

```bash
# Production
export SLACK_ENV=production

# Staging
export SLACK_ENV=staging
```

Le code charge automatiquement `config/${SLACK_ENV}.json`

### Logging Avancé

```json
{
  "logging": {
    "level": "INFO",
    "file": "logs/slack-toolbox.log",
    "max_bytes": 10485760,
    "backup_count": 5,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  }
}
```

---

## 🐛 Dépannage Configuration

### Erreur : "Invalid token"

- Vérifiez que le token commence par `xoxb-`
- Régénérez le token depuis l'app Slack
- Vérifiez que l'app est installée dans le workspace

### Erreur : "Missing permissions"

- Ajoutez les scopes manquants dans l'app
- Réinstallez l'app dans le workspace
- Vérifiez avec `make audit-permissions`

### Erreur : "Rate limited"

- Augmentez `rate_limit_delay` dans config
- Réduisez le nombre d'appels simultanés
- Utilisez le mode batch pour les grosses opérations

### Webhook ne fonctionne pas

- Vérifiez l'URL (doit être HTTPS)
- Testez avec : `curl -X POST -H 'Content-type: application/json' --data '{"text":"Test"}' WEBHOOK_URL`
- Vérifiez que le canal existe toujours

---

## 📚 Prochaines Étapes

Configuration terminée ! Passez à :

- **[Utilisation](./UTILISATION.md)** - Apprendre à utiliser les outils
- **[Sécurité](./SECURITE.md)** - Bonnes pratiques de sécurité
- **[FAQ](./FAQ.md)** - Questions fréquentes

---

**Besoin d'aide ?** Consultez la [FAQ](./FAQ.md) ou ouvrez une [issue](https://github.com/GitCroque/slack-toolbox/issues).
