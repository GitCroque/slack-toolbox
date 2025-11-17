# FAQ et Troubleshooting

Guide de dépannage et questions fréquentes pour Slack Management Platform.

## 📋 Table des matières

- [Installation](#installation)
- [Configuration](#configuration)
- [Erreurs courantes](#erreurs-courantes)
- [Permissions](#permissions)
- [Performance](#performance)
- [Utilisation](#utilisation)

---

## Installation

### ❓ Python 3.8+ requis mais j'ai une version plus ancienne

**Solution:**

Sur macOS:
```bash
# Installer Python 3 via Homebrew
brew install python@3.11

# Vérifier la version
python3 --version
```

### ❓ `pip3 install -r requirements.txt` échoue

**Solutions:**

1. **Mettre à jour pip:**
```bash
python3 -m pip install --upgrade pip
```

2. **Utiliser un environnement virtuel:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Installation manuelle:**
```bash
pip3 install slack-sdk requests
```

### ❓ `Module not found: slack_sdk`

**Solution:**
```bash
pip3 install slack-sdk
# ou
python3 -m pip install slack-sdk
```

---

## Configuration

### ❓ Où trouver mon token Slack ?

1. Allez sur https://api.slack.com/apps
2. Sélectionnez votre app (ou créez-en une)
3. **OAuth & Permissions** → **Bot User OAuth Token**
4. Copiez le token (commence par `xoxb-`)

### ❓ Mon token ne fonctionne pas

**Vérifications:**

1. **Token correct:**
   - Doit commencer par `xoxb-` (Bot Token)
   - Pas d'espaces avant/après
   - Guillemets corrects dans le JSON

2. **App installée:**
   - L'app doit être installée dans le workspace
   - Réinstaller si nécessaire

3. **Permissions:**
   - Vérifier que les scopes requis sont ajoutés
   - Réinstaller l'app après ajout de scopes

**Test:**
```bash
make test
# ou
python3 scripts/utils/test_connection.py
```

### ❓ `Configuration file not found`

**Solution:**
```bash
# Créer le fichier de config
cp config/config.example.json config/config.json

# Éditer avec votre token
nano config/config.json
```

### ❓ Comment protéger mon token ?

1. **Ne JAMAIS commiter `config/config.json`**
   - Déjà dans `.gitignore`

2. **Permissions fichier:**
```bash
chmod 600 config/config.json
```

3. **Rotation régulière:**
   - Regénérer le token tous les 3-6 mois

---

## Erreurs courantes

### ❓ `invalid_auth` ou `not_authed`

**Causes:**
- Token invalide ou expiré
- Token non copié correctement
- App non installée

**Solution:**
1. Vérifier le token dans config/config.json
2. Réinstaller l'app dans le workspace
3. Générer un nouveau token si nécessaire

### ❓ `missing_scope`

**Erreur:**
```
SlackApiError: missing_scope: admin.users:read
```

**Solution:**
1. Aller dans votre app sur api.slack.com
2. **OAuth & Permissions** → **Scopes**
3. Ajouter le scope manquant (ex: `admin.users:read`)
4. **Réinstaller l'app** dans le workspace
5. Copier le nouveau token

### ❓ `ratelimited` - Too many requests

**Causes:**
- Trop de requêtes trop rapidement
- Limite API Slack atteinte

**Solutions:**

1. **Attendre:**
   - Le script attend automatiquement et retry

2. **Réduire la vitesse:**
```python
# Dans lib/slack_client.py, augmenter le délai
self.rate_limit_delay = 2  # Au lieu de 1
```

3. **Traiter en batch:**
   - Utiliser `--dry-run` d'abord
   - Traiter en plusieurs fois

### ❓ `channel_not_found` ou `user_not_found`

**Causes:**
- ID/nom incorrect
- Utilisateur désactivé
- Canal archivé

**Solutions:**

1. **Vérifier le nom:**
```bash
# Lister tous les canaux
make list-channels

# Rechercher
make search QUERY="nom-du-canal"
```

2. **Inclure les archivés:**
```bash
python3 scripts/channels/list_channels.py --include-archived
```

### ❓ `CSV parsing error`

**Causes:**
- Format CSV invalide
- Encodage incorrect
- Virgules dans les données

**Solutions:**

1. **Valider le CSV:**
```bash
make validate-csv FILE=users.csv
```

2. **Utiliser le template:**
```bash
make template TYPE=users
```

3. **Vérifier l'encodage:**
   - Le fichier doit être en UTF-8

4. **Échapper les virgules:**
   - Mettre les champs entre guillemets: `"Nom, Prénom"`

---

## Permissions

### ❓ Quelles permissions sont nécessaires ?

**Minimum requis:**
```
users:read
users:read.email
channels:read
team:read
```

**Pour gestion complète:**
```
admin.users:read
admin.users:write
channels:write
channels:manage
groups:read
groups:write
files:read
```

### ❓ J'ai des permissions mais ça ne marche pas

**Solution:**

1. **Réinstaller l'app:**
   - Les scopes ne s'appliquent qu'après réinstallation

2. **Vérifier le rôle:**
   - Certaines actions nécessitent d'être Owner/Admin du workspace

3. **Tester les permissions:**
```python
python3 -c "
from lib.slack_client import SlackManager
slack = SlackManager()
slack.test_connection()
"
```

### ❓ `restricted_action` error

**Cause:**
- Votre compte n'a pas les droits suffisants

**Solution:**
- Demander à un Owner/Admin d'installer l'app
- Ou obtenir les droits Admin sur le workspace

---

## Performance

### ❓ Les scripts sont lents

**Causes:**
- Beaucoup d'utilisateurs/canaux
- Rate limiting
- Réseau lent

**Optimisations:**

1. **Limiter les résultats:**
```bash
# Au lieu de tout exporter
python3 scripts/users/list_users.py | head -50
```

2. **Éviter les opérations lourdes:**
   - Ne pas inclure `--with-members` sauf si nécessaire
   - Limiter `--message-limit` dans les backups

3. **Utiliser les filtres:**
```bash
# Filtrer par rôle
python3 scripts/users/list_users.py --role admin
```

### ❓ Timeout lors du backup avec messages

**Solution:**

1. **Réduire la limite:**
```bash
python3 scripts/utils/full_backup.py --include-messages --message-limit 100
```

2. **Backup par canal:**
```bash
# Backup canal par canal
for channel in general random; do
    python3 scripts/audit/export_channel_history.py --channel $channel
done
```

3. **Augmenter le timeout:**
```python
# Dans le script, modifier
response = slack.get_channel_history(timeout=300)  # 5 minutes
```

---

## Utilisation

### ❓ Comment inviter plusieurs utilisateurs ?

1. **Créer un CSV:**
```bash
make template TYPE=users
```

2. **Éditer le fichier:**
```csv
email,first_name,last_name,channels
john@example.com,John,Doe,"general,random"
jane@example.com,Jane,Smith,general
```

3. **Valider:**
```bash
make validate-csv FILE=users.csv
```

4. **Inviter:**
```bash
make invite-users FILE=users.csv
```

### ❓ Comment tester sans faire de changements ?

**Utiliser `--dry-run`:**

```bash
# Invitation en dry-run
python3 scripts/users/invite_users.py --file users.csv --dry-run

# Création de canaux en dry-run
python3 scripts/channels/create_channels.py --file channels.csv --dry-run
```

### ❓ Comment automatiser les tâches ?

**Utiliser cron:**

```bash
# Éditer crontab
crontab -e

# Ajouter un backup quotidien à 2h
0 2 * * * /path/to/slack-script/cron/daily_backup.sh
```

Voir `cron/README.md` pour plus d'exemples.

### ❓ Comment exporter toutes les données ?

```bash
# Backup complet avec messages
make backup-full

# Ou
python3 scripts/utils/full_backup.py --include-messages --message-limit 1000
```

### ❓ Comment voir les statistiques du workspace ?

```bash
# Statistiques dans le terminal
make stats

# Dashboard HTML
make dashboard
# Puis ouvrir dashboard.html dans un navigateur
```

### ❓ Comment chercher un utilisateur ?

```bash
# Recherche universelle
make search QUERY="john"

# Recherche uniquement utilisateurs
make search QUERY="john" TYPE=user

# Par email
make search QUERY="@example.com"
```

---

## Problèmes macOS spécifiques

### ❓ `command not found: python3`

**Solution:**
```bash
# Installer Python via Homebrew
brew install python3

# Ou utiliser python au lieu de python3
alias python3=python
```

### ❓ SSL certificate errors

**Solution:**
```bash
# Installer les certificats
/Applications/Python\ 3.x/Install\ Certificates.command

# Ou
pip3 install --upgrade certifi
```

### ❓ Permission denied lors de l'installation

**Solution:**
```bash
# Utiliser --user
pip3 install --user -r requirements.txt

# Ou environnement virtuel
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Dépannage avancé

### ❓ Comment activer les logs détaillés ?

**Ajouter dans votre script:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Ou utiliser:**
```bash
python3 -v script.py  # Verbose mode
```

### ❓ Comment débugger les requêtes API ?

```python
from lib.slack_client import SlackManager
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('slack_sdk')
logger.setLevel(logging.DEBUG)

slack = SlackManager()
# Toutes les requêtes HTTP seront loggées
```

### ❓ Les fichiers générés sont où ?

```
slack-script/
├── backups/          # Backups
├── exports/          # Exports CSV/JSON
├── logs/             # Logs des scripts
└── dashboard.html    # Dashboard généré
```

---

## Questions de sécurité

### ❓ Est-ce sûr de stocker mon token en local ?

**Recommandations:**

1. **Permissions fichier:**
```bash
chmod 600 config/config.json
```

2. **Chiffrement disque:**
   - Activer FileVault sur macOS

3. **Variables d'environnement:**
```bash
export SLACK_TOKEN="xoxb-..."
# Modifier les scripts pour lire depuis $SLACK_TOKEN
```

### ❓ Mon token a fuité, que faire ?

**Actions immédiates:**

1. **Révoquer le token:**
   - api.slack.com → Your App → OAuth & Permissions → Revoke

2. **Générer un nouveau token:**
   - Réinstaller l'app

3. **Vérifier les logs:**
   - Chercher des activités suspectes dans Slack

4. **Mettre à jour config.json:**
   - Avec le nouveau token

---

## Support additionnel

### 📚 Documentation

- **README.md** - Documentation principale
- **QUICKSTART.md** - Démarrage rapide
- **SLACK_API_GUIDE.md** - Guide API complet
- **examples/EXAMPLES.md** - Exemples d'utilisation

### 🔗 Liens utiles

- **Documentation Slack API:** https://api.slack.com/
- **Slack SDK Python:** https://slack.dev/python-slack-sdk/
- **Issues GitHub:** https://github.com/GitCroque/slack-script/issues

### 💡 Besoin d'aide ?

1. Vérifiez cette FAQ
2. Consultez les logs dans `logs/`
3. Testez avec `--dry-run`
4. Ouvrez une issue sur GitHub

---

**Dernière mise à jour:** 2025-11-15
