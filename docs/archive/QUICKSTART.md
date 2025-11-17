# Guide de démarrage rapide

Ce guide vous aidera à configurer et utiliser les scripts de gestion Slack en quelques minutes.

## 📋 Prérequis

- macOS à jour
- Python 3.8 ou supérieur (généralement pré-installé sur macOS)
- Un compte Slack avec permissions administrateur
- Une offre payante Slack (requis pour certaines fonctionnalités avancées)

## 🚀 Installation rapide

### 1. Cloner le repository

```bash
git clone https://github.com/GitCroque/slack-script.git
cd slack-script
```

### 2. Installer les dépendances Python

```bash
pip3 install -r requirements.txt
```

Si vous n'avez pas pip3, installez-le d'abord :

```bash
python3 -m ensurepip --upgrade
```

### 3. Créer votre application Slack

1. Visitez https://api.slack.com/apps
2. Cliquez sur **"Create New App"**
3. Choisissez **"From scratch"**
4. Donnez un nom à votre app (ex: "Workspace Manager")
5. Sélectionnez votre workspace Slack

### 4. Configurer les permissions (Scopes)

Dans votre application Slack :

1. Allez dans **"OAuth & Permissions"**
2. Descendez jusqu'à **"Scopes"**
3. Ajoutez les **Bot Token Scopes** suivants :

**Permissions utilisateurs :**
- `users:read` - Lire les informations utilisateurs
- `users:read.email` - Lire les emails des utilisateurs
- `admin.users:read` - Admin: lire les utilisateurs
- `admin.users:write` - Admin: gérer les utilisateurs

**Permissions canaux :**
- `channels:read` - Lire les canaux publics
- `channels:write` - Gérer les canaux publics
- `channels:manage` - Gérer les canaux (archiver, etc.)
- `channels:history` - Lire l'historique des messages
- `groups:read` - Lire les canaux privés
- `groups:write` - Gérer les canaux privés
- `groups:history` - Lire l'historique des canaux privés

**Permissions fichiers :**
- `files:read` - Lire les fichiers

**Permissions workspace :**
- `team:read` - Lire les informations du workspace
- `emoji:read` - Lire les emojis personnalisés

### 5. Installer l'application dans votre workspace

1. Toujours dans **"OAuth & Permissions"**
2. Cliquez sur **"Install to Workspace"**
3. Autorisez l'application
4. **IMPORTANT** : Copiez le **"Bot User OAuth Token"** (commence par `xoxb-`)

### 6. Configurer le token

```bash
# Copier le fichier de configuration exemple
cp config/config.example.json config/config.json

# Éditer avec votre éditeur préféré (nano, vim, ou VSCode)
nano config/config.json
```

Remplacez `"xoxb-your-bot-token-here"` par votre token copié à l'étape 5 :

```json
{
  "slack_token": "xoxb-YOUR-ACTUAL-TOKEN-HERE",
  "workspace_name": "VotreSociete",
  "default_export_format": "csv",
  "timezone": "Europe/Paris"
}
```

### 7. Tester la connexion

```bash
python3 scripts/utils/test_connection.py
```

Vous devriez voir :
```
✅ Connected to Slack workspace: VotreSociete
   Bot user: workspace-manager
```

## ✨ Premiers pas

### Afficher les statistiques de votre workspace

```bash
python3 scripts/utils/workspace_stats.py
```

### Lister tous les utilisateurs

```bash
python3 scripts/users/list_users.py
```

### Lister tous les canaux

```bash
python3 scripts/channels/list_channels.py
```

### Créer un backup

```bash
python3 scripts/utils/full_backup.py
```

## 📚 Prochaines étapes

Consultez :
- [README.md](README.md) - Documentation complète
- [examples/EXAMPLES.md](examples/EXAMPLES.md) - Exemples d'utilisation détaillés

## 🆘 Problèmes courants

### "Module not found: slack_sdk"

```bash
pip3 install slack-sdk
```

### "Permission denied"

Rendez les scripts exécutables :

```bash
chmod +x scripts/**/*.py
```

### "Configuration file not found"

Assurez-vous d'avoir créé `config/config.json` :

```bash
cp config/config.example.json config/config.json
```

### "Invalid authentication"

Vérifiez que :
1. Votre token commence bien par `xoxb-`
2. Il n'y a pas d'espaces avant/après le token dans config.json
3. L'application est bien installée dans votre workspace
4. Les permissions (scopes) sont correctement configurées

### "Missing scope: admin.users:read"

Retournez dans votre app Slack sur https://api.slack.com/apps, ajoutez les scopes manquants, puis **réinstallez** l'app dans votre workspace.

## 💡 Astuces

### Utiliser un alias pour simplifier les commandes

Ajoutez à votre `~/.zshrc` ou `~/.bash_profile` :

```bash
alias slack-users='python3 /chemin/vers/slack-script/scripts/users/list_users.py'
alias slack-channels='python3 /chemin/vers/slack-script/scripts/channels/list_channels.py'
alias slack-stats='python3 /chemin/vers/slack-script/scripts/utils/workspace_stats.py'
```

Puis rechargez :
```bash
source ~/.zshrc  # ou source ~/.bash_profile
```

Maintenant vous pouvez simplement taper :
```bash
slack-users
slack-stats
```

## 🔒 Sécurité

- **Ne commitez JAMAIS** votre `config/config.json`
- Gardez votre token secret
- Rotez le token régulièrement (via l'app Slack sur api.slack.com)
- Utilisez des permissions minimales nécessaires

## 📞 Support

- Issues GitHub : https://github.com/GitCroque/slack-script/issues
- Documentation Slack API : https://api.slack.com/

Bon management de votre Slack ! 🚀
