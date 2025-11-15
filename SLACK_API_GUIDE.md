# Guide complet de l'API Slack

Ce guide vous explique comment utiliser l'API Slack, comment elle fonctionne, et comment développer vos propres scripts.

## 📚 Table des matières

1. [Introduction à l'API Slack](#introduction)
2. [Concepts fondamentaux](#concepts-fondamentaux)
3. [Authentification et tokens](#authentification)
4. [Permissions et scopes](#permissions-et-scopes)
5. [Utilisation du SDK Python](#sdk-python)
6. [Méthodes API principales](#méthodes-api)
7. [Gestion des erreurs](#gestion-des-erreurs)
8. [Rate limiting et bonnes pratiques](#rate-limiting)
9. [Exemples pratiques](#exemples-pratiques)
10. [Debugging et troubleshooting](#debugging)

---

## Introduction

### Qu'est-ce que l'API Slack ?

L'API Slack est une interface REST qui permet d'interagir programmatiquement avec un workspace Slack. Elle vous permet de :

- Gérer les utilisateurs et leurs profils
- Créer et gérer des canaux
- Envoyer et lire des messages
- Gérer les fichiers
- Automatiser des tâches administratives
- Créer des intégrations personnalisées

### Types d'API Slack

1. **Web API** - API REST principale (ce que nous utilisons)
2. **Events API** - Recevoir des événements en temps réel
3. **RTM API** - Communication en temps réel (deprecated)
4. **Conversations API** - Gérer les conversations
5. **Admin API** - Gestion avancée (Enterprise Grid)

---

## Concepts fondamentaux

### Architecture de l'API

```
Votre Application
       ↓
   Slack SDK
       ↓
  HTTPS Request
       ↓
   API Slack
       ↓
  Workspace Slack
```

### Éléments clés

#### 1. **Workspace** (ou Team)
- Votre environnement Slack
- Identifié par un Team ID (ex: `T1234567890`)

#### 2. **App Slack**
- Application que vous créez sur api.slack.com
- Contient vos tokens et permissions
- Peut être installée dans un ou plusieurs workspaces

#### 3. **Tokens**
- **Bot Token** (`xoxb-...`) - Pour les actions automatisées
- **User Token** (`xoxp-...`) - Agit au nom d'un utilisateur
- **App Token** (`xapp-...`) - Pour Socket Mode

#### 4. **Scopes** (Permissions)
- Définissent ce que votre app peut faire
- Doivent être définis AVANT d'installer l'app
- Exemple : `users:read`, `channels:write`

#### 5. **IDs**
Slack utilise des IDs uniques pour tout :
- User ID : `U1234567890`
- Channel ID : `C1234567890`
- Team ID : `T1234567890`
- Message timestamp : `1234567890.123456`

---

## Authentification

### Créer une application Slack

#### Étape 1 : Créer l'app

1. Allez sur https://api.slack.com/apps
2. Cliquez sur **"Create New App"**
3. Choisissez **"From scratch"**
4. Donnez un nom (ex: "Workspace Manager")
5. Sélectionnez votre workspace

#### Étape 2 : Configurer les permissions (OAuth Scopes)

Dans **OAuth & Permissions** → **Bot Token Scopes**, ajoutez :

```
Permissions de base :
- users:read          # Lire les infos utilisateurs
- users:read.email    # Lire les emails
- channels:read       # Lire les canaux publics
- groups:read         # Lire les canaux privés
- team:read           # Lire les infos workspace

Permissions administrateur :
- admin.users:read    # Admin: lire les utilisateurs
- admin.users:write   # Admin: gérer les utilisateurs
- channels:write      # Gérer les canaux
- channels:manage     # Actions avancées canaux
```

#### Étape 3 : Installer l'app

1. Cliquez sur **"Install to Workspace"**
2. Autorisez les permissions
3. Copiez le **Bot User OAuth Token**

#### Étape 4 : Sécuriser votre token

```bash
# Ne JAMAIS commiter votre token !
# Stockez-le dans config.json (gitignored)

{
  "slack_token": "xoxb-YOUR-BOT-TOKEN-HERE"
}
```

### Types de tokens

#### Bot Token (xoxb-...)
```python
# Recommandé pour la plupart des cas
# Agit au nom de votre bot
# Permissions définies par les scopes de l'app

client = WebClient(token="xoxb-YOUR-TOKEN")
```

#### User Token (xoxp-...)
```python
# Agit au nom d'un utilisateur spécifique
# Utilisé pour des actions "comme si c'était l'utilisateur"
# Plus de risques de sécurité

client = WebClient(token="xoxp-YOUR-USER-TOKEN")
```

---

## Permissions et scopes

### Catégories de scopes

#### **Users** - Gestion des utilisateurs
```
users:read              # Lire les profils utilisateurs
users:read.email        # Lire les emails des utilisateurs
users:write             # Modifier les profils
admin.users:read        # Admin: liste détaillée
admin.users:write       # Admin: inviter, désactiver
```

#### **Channels** - Gestion des canaux
```
channels:read           # Lister les canaux publics
channels:write          # Créer/modifier des canaux
channels:manage         # Archiver, renommer
channels:history        # Lire l'historique des messages
channels:join           # Rejoindre des canaux
```

#### **Groups** - Canaux privés
```
groups:read             # Lister les canaux privés
groups:write            # Créer/modifier des canaux privés
groups:history          # Lire l'historique
```

#### **Messages** - Envoi de messages
```
chat:write              # Envoyer des messages
chat:write.public       # Envoyer dans canaux publics
chat:write.customize    # Personnaliser nom/avatar
```

#### **Files** - Gestion des fichiers
```
files:read              # Lire les infos fichiers
files:write             # Upload des fichiers
```

#### **Team** - Informations workspace
```
team:read               # Infos sur le workspace
emoji:read              # Lister les emojis personnalisés
```

### Vérifier les scopes requis

```python
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

client = WebClient(token="xoxb-YOUR-TOKEN")

try:
    # Cette méthode teste votre connexion et montre vos scopes
    response = client.auth_test()
    print("User ID:", response['user_id'])
    print("Team:", response['team'])

    # Pour voir tous les scopes disponibles
    response = client.api_test()

except SlackApiError as e:
    print(f"Erreur: {e.response['error']}")
    if e.response['error'] == 'missing_scope':
        print(f"Scope requis: {e.response.get('needed')}")
```

---

## SDK Python

### Installation

```bash
pip3 install slack-sdk
```

### Utilisation de base

#### 1. Initialisation du client

```python
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Créer le client
client = WebClient(token="xoxb-YOUR-TOKEN")

# Tester la connexion
try:
    response = client.auth_test()
    print(f"✅ Connecté à: {response['team']}")
except SlackApiError as e:
    print(f"❌ Erreur: {e.response['error']}")
```

#### 2. Structure d'une requête API

```python
# Format général
response = client.nom_de_methode(
    parametre1="valeur1",
    parametre2="valeur2"
)

# Exemple concret
response = client.users_list(
    limit=100,
    cursor="dXNlcjpVMEc5V0ZYTlo="
)

# Le résultat est un dictionnaire
print(response['ok'])        # True si succès
print(response['members'])   # Les données
```

#### 3. Gestion de la pagination

Beaucoup de méthodes API retournent des résultats paginés :

```python
def get_all_users(client):
    """Récupère tous les utilisateurs avec pagination"""
    all_users = []
    cursor = None

    while True:
        # Faire la requête avec le curseur
        response = client.users_list(
            cursor=cursor,
            limit=200  # Maximum par page
        )

        # Ajouter les résultats
        all_users.extend(response['members'])

        # Vérifier s'il y a d'autres pages
        cursor = response.get('response_metadata', {}).get('next_cursor')
        if not cursor:
            break

    return all_users

# Utilisation
users = get_all_users(client)
print(f"Total: {len(users)} utilisateurs")
```

#### 4. Gestion des erreurs

```python
from slack_sdk.errors import SlackApiError
import time

def api_call_with_retry(client, method, max_retries=3, **kwargs):
    """Appel API avec retry automatique"""

    for attempt in range(max_retries):
        try:
            # Appeler la méthode API
            response = getattr(client, method)(**kwargs)
            return response

        except SlackApiError as e:
            error = e.response['error']

            # Rate limiting
            if error == 'ratelimited':
                retry_after = int(e.response.headers.get('Retry-After', 60))
                print(f"⏳ Rate limited. Attente de {retry_after}s...")
                time.sleep(retry_after)
                continue

            # Erreur de permission
            elif error == 'missing_scope':
                needed = e.response.get('needed', 'unknown')
                print(f"❌ Permission manquante: {needed}")
                raise

            # Ressource non trouvée
            elif error in ['user_not_found', 'channel_not_found']:
                print(f"❌ Ressource non trouvée")
                return None

            # Erreur réseau - retry
            elif error in ['timeout', 'service_unavailable']:
                if attempt < max_retries - 1:
                    wait = 2 ** attempt  # Backoff exponentiel
                    print(f"⚠️  Erreur réseau. Retry dans {wait}s...")
                    time.sleep(wait)
                    continue

            # Autre erreur
            else:
                print(f"❌ Erreur API: {error}")
                raise

# Utilisation
response = api_call_with_retry(
    client,
    'users_list',
    limit=100
)
```

---

## Méthodes API principales

### 👥 Users (Utilisateurs)

#### Lister les utilisateurs

```python
# Liste simple
response = client.users_list()
users = response['members']

for user in users:
    print(f"{user['name']}: {user['profile']['email']}")

# Avec pagination
def get_all_users():
    users = []
    cursor = None

    while True:
        response = client.users_list(cursor=cursor, limit=200)
        users.extend(response['members'])

        cursor = response.get('response_metadata', {}).get('next_cursor')
        if not cursor:
            break

    return users
```

#### Rechercher un utilisateur par email

```python
response = client.users_lookupByEmail(
    email="john@example.com"
)

user = response['user']
print(f"ID: {user['id']}")
print(f"Nom: {user['real_name']}")
```

#### Obtenir les infos d'un utilisateur

```python
response = client.users_info(
    user="U1234567890"  # User ID
)

user = response['user']
profile = user['profile']

print(f"Email: {profile['email']}")
print(f"Titre: {profile.get('title', 'N/A')}")
print(f"Téléphone: {profile.get('phone', 'N/A')}")
```

#### Inviter un utilisateur (Admin)

```python
response = client.admin_users_invite(
    email="newuser@example.com",
    team_id="T1234567890",
    channel_ids="C1234567890,C0987654321",  # Canaux à rejoindre
    real_name="John Doe"
)

print(f"Utilisateur invité: {response['user']['email']}")
```

#### Désactiver un utilisateur (Admin)

```python
response = client.admin_users_remove(
    user_id="U1234567890",
    team_id="T1234567890"
)

print("✅ Utilisateur désactivé")
```

### 📢 Channels (Canaux)

#### Lister les canaux

```python
# Canaux publics et privés
response = client.conversations_list(
    types="public_channel,private_channel",
    exclude_archived=True,
    limit=200
)

channels = response['channels']

for channel in channels:
    ch_type = "Privé" if channel['is_private'] else "Public"
    print(f"#{channel['name']} ({ch_type}): {channel['num_members']} membres")
```

#### Créer un canal

```python
# Canal public
response = client.conversations_create(
    name="nouveau-projet",
    is_private=False
)

channel = response['channel']
print(f"✅ Canal créé: #{channel['name']} (ID: {channel['id']})")

# Ajouter une description
client.conversations_setTopic(
    channel=channel['id'],
    topic="Discussion sur le nouveau projet"
)
```

#### Archiver un canal

```python
response = client.conversations_archive(
    channel="C1234567890"
)

print("✅ Canal archivé")
```

#### Désarchiver un canal

```python
response = client.conversations_unarchive(
    channel="C1234567890"
)

print("✅ Canal désarchivé")
```

#### Lister les membres d'un canal

```python
members = []
cursor = None

while True:
    response = client.conversations_members(
        channel="C1234567890",
        cursor=cursor,
        limit=200
    )

    members.extend(response['members'])

    cursor = response.get('response_metadata', {}).get('next_cursor')
    if not cursor:
        break

print(f"Membres: {len(members)}")
```

#### Inviter des utilisateurs dans un canal

```python
# Inviter un ou plusieurs utilisateurs
response = client.conversations_invite(
    channel="C1234567890",
    users="U1111111111,U2222222222,U3333333333"  # Virgule-séparés
)

print("✅ Utilisateurs ajoutés au canal")
```

#### Retirer un utilisateur d'un canal

```python
response = client.conversations_kick(
    channel="C1234567890",
    user="U1234567890"
)

print("✅ Utilisateur retiré du canal")
```

### 💬 Messages

#### Envoyer un message

```python
response = client.chat_postMessage(
    channel="C1234567890",  # Ou "#general"
    text="Hello, World!",
    as_user=True
)

print(f"Message envoyé: {response['ts']}")
```

#### Message avec formatage

```python
response = client.chat_postMessage(
    channel="#general",
    text="Message avec formatage",
    blocks=[
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Titre en gras*\n\nTexte normal avec _italique_ et ~barré~"
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": "*Priorité:*\nHaute"},
                {"type": "mrkdwn", "text": "*Status:*\nEn cours"}
            ]
        }
    ]
)
```

#### Lire l'historique d'un canal

```python
response = client.conversations_history(
    channel="C1234567890",
    limit=100,
    oldest="1234567890.123456",  # Timestamp optionnel
    latest="1234567890.123456"   # Timestamp optionnel
)

messages = response['messages']

for msg in messages:
    user = msg.get('user', 'Bot')
    text = msg.get('text', '')
    ts = msg.get('ts', '')
    print(f"[{ts}] {user}: {text}")
```

### 📁 Files

#### Lister les fichiers

```python
response = client.files_list(
    count=100,
    user="U1234567890",  # Optionnel: filtrer par utilisateur
    channel="C1234567890"  # Optionnel: filtrer par canal
)

files = response['files']

for file in files:
    print(f"{file['name']}: {file['size']} bytes")
```

#### Upload un fichier

```python
response = client.files_upload(
    channels="#general",
    file="./rapport.pdf",
    title="Rapport mensuel",
    initial_comment="Voici le rapport du mois"
)

print(f"✅ Fichier uploadé: {response['file']['name']}")
```

### 🏢 Workspace (Team)

#### Informations du workspace

```python
response = client.team_info()
team = response['team']

print(f"Nom: {team['name']}")
print(f"Domaine: {team['domain']}")
print(f"Email domain: {team['email_domain']}")
```

#### Lister les emojis personnalisés

```python
response = client.emoji_list()
emojis = response['emoji']

for name, url in emojis.items():
    print(f":{name}: → {url}")
```

---

## Gestion des erreurs

### Codes d'erreur courants

```python
from slack_sdk.errors import SlackApiError

try:
    response = client.users_info(user="U1234567890")

except SlackApiError as e:
    error_code = e.response['error']

    if error_code == 'user_not_found':
        print("❌ Utilisateur introuvable")

    elif error_code == 'missing_scope':
        needed_scope = e.response.get('needed', 'unknown')
        print(f"❌ Permission manquante: {needed_scope}")

    elif error_code == 'invalid_auth':
        print("❌ Token invalide ou expiré")

    elif error_code == 'account_inactive':
        print("❌ Compte désactivé")

    elif error_code == 'not_authed':
        print("❌ Non authentifié")

    elif error_code == 'ratelimited':
        retry_after = e.response.headers.get('Retry-After', '60')
        print(f"❌ Rate limit atteint. Réessayer dans {retry_after}s")

    else:
        print(f"❌ Erreur: {error_code}")
```

### Wrapper de gestion d'erreurs

```python
import time
from functools import wraps

def handle_api_errors(max_retries=3):
    """Décorateur pour gérer automatiquement les erreurs API"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)

                except SlackApiError as e:
                    error = e.response['error']

                    # Retry sur rate limit
                    if error == 'ratelimited':
                        retry_after = int(e.response.headers.get('Retry-After', 60))
                        print(f"Rate limited. Attente {retry_after}s...")
                        time.sleep(retry_after)
                        continue

                    # Retry sur erreur temporaire
                    elif error in ['timeout', 'service_unavailable']:
                        if attempt < max_retries - 1:
                            wait = 2 ** attempt
                            print(f"Erreur temporaire. Retry dans {wait}s...")
                            time.sleep(wait)
                            continue

                    # Autres erreurs: ne pas retry
                    raise

            raise Exception(f"Échec après {max_retries} tentatives")

        return wrapper
    return decorator

# Utilisation
@handle_api_errors(max_retries=3)
def get_user(client, user_id):
    response = client.users_info(user=user_id)
    return response['user']
```

---

## Rate limiting

### Comprendre les limites

Slack impose des limites de débit (rate limits) :

- **Tier 1** : 1+ requêtes par minute (méthodes simples)
- **Tier 2** : 20+ requêtes par minute (méthodes de lecture)
- **Tier 3** : 50+ requêtes par minute (méthodes avancées)
- **Tier 4** : 100+ requêtes par minute (méthodes spéciales)

### Headers de rate limit

```python
response = client.users_list()

# Vérifier les headers de rate limit
headers = response.headers

rate_limit = headers.get('X-Rate-Limit-Limit')      # Limite totale
remaining = headers.get('X-Rate-Limit-Remaining')   # Requêtes restantes
reset_time = headers.get('X-Rate-Limit-Reset')      # Timestamp de reset

print(f"Limite: {rate_limit}")
print(f"Restant: {remaining}")
print(f"Reset: {reset_time}")
```

### Implémentation d'un rate limiter

```python
import time
from datetime import datetime

class RateLimiter:
    """Gère le rate limiting pour l'API Slack"""

    def __init__(self, calls_per_second=1):
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0

    def wait_if_needed(self):
        """Attendre si nécessaire pour respecter le rate limit"""
        elapsed = time.time() - self.last_call

        if elapsed < self.min_interval:
            sleep_time = self.min_interval - elapsed
            time.sleep(sleep_time)

        self.last_call = time.time()

# Utilisation
rate_limiter = RateLimiter(calls_per_second=1)

for user_id in user_ids:
    rate_limiter.wait_if_needed()
    response = client.users_info(user=user_id)
    # Traiter la réponse...
```

### Traitement par batch

```python
def process_in_batches(items, batch_size=50, delay=1.0):
    """Traiter des items par lots avec délai"""

    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]

        # Traiter le batch
        for item in batch:
            # Votre traitement ici
            pass

        # Attendre entre les batchs (sauf pour le dernier)
        if i + batch_size < len(items):
            print(f"Traité {i + batch_size}/{len(items)}. Attente {delay}s...")
            time.sleep(delay)

# Exemple: inviter des utilisateurs par batch
emails = ["user1@example.com", "user2@example.com", ...]

for i in range(0, len(emails), 10):
    batch = emails[i:i+10]

    for email in batch:
        try:
            client.admin_users_invite(email=email, team_id="T123")
        except SlackApiError as e:
            print(f"Erreur pour {email}: {e.response['error']}")

    # Pause entre les batches
    if i + 10 < len(emails):
        time.sleep(1)
```

---

## Exemples pratiques

### Exemple 1 : Script d'onboarding automatisé

```python
#!/usr/bin/env python3
"""
Script d'onboarding: invite des utilisateurs et les ajoute aux canaux
"""

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import csv

def onboard_users(client, csv_file):
    """
    Onboard des utilisateurs depuis un CSV

    CSV format: email,first_name,last_name,channels
    """

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            email = row['email']
            channels = row['channels'].split(',')

            print(f"\n📥 Onboarding: {email}")

            try:
                # 1. Vérifier si l'utilisateur existe déjà
                try:
                    user = client.users_lookupByEmail(email=email)
                    user_id = user['user']['id']
                    print(f"  ℹ️  Utilisateur existe déjà (ID: {user_id})")
                except SlackApiError as e:
                    if e.response['error'] == 'users_not_found':
                        # 2. Inviter l'utilisateur
                        print("  ➕ Invitation en cours...")
                        response = client.admin_users_invite(
                            email=email,
                            team_id="T1234567890",
                            real_name=f"{row['first_name']} {row['last_name']}"
                        )
                        user_id = response['user']['id']
                        print(f"  ✅ Utilisateur invité (ID: {user_id})")
                    else:
                        raise

                # 3. Ajouter aux canaux
                for channel_name in channels:
                    channel_name = channel_name.strip()

                    # Trouver l'ID du canal
                    channels_list = client.conversations_list()
                    channel = next(
                        (ch for ch in channels_list['channels']
                         if ch['name'] == channel_name),
                        None
                    )

                    if channel:
                        try:
                            client.conversations_invite(
                                channel=channel['id'],
                                users=user_id
                            )
                            print(f"  ✅ Ajouté à #{channel_name}")
                        except SlackApiError as e:
                            if e.response['error'] == 'already_in_channel':
                                print(f"  ℹ️  Déjà dans #{channel_name}")
                            else:
                                print(f"  ❌ Erreur #{channel_name}: {e.response['error']}")
                    else:
                        print(f"  ⚠️  Canal #{channel_name} introuvable")

            except SlackApiError as e:
                print(f"  ❌ Erreur: {e.response['error']}")

# Utilisation
if __name__ == '__main__':
    client = WebClient(token="xoxb-YOUR-TOKEN")
    onboard_users(client, "new_employees.csv")
```

### Exemple 2 : Nettoyer les canaux inactifs

```python
#!/usr/bin/env python3
"""
Trouver et archiver les canaux inactifs
"""

from slack_sdk import WebClient
from datetime import datetime, timedelta

def find_inactive_channels(client, days=90):
    """Trouve les canaux sans activité depuis X jours"""

    cutoff_date = datetime.now() - timedelta(days=days)
    cutoff_ts = cutoff_date.timestamp()

    # Lister tous les canaux actifs
    response = client.conversations_list(
        exclude_archived=True,
        types="public_channel"
    )

    inactive = []

    for channel in response['channels']:
        channel_id = channel['id']
        channel_name = channel['name']

        # Récupérer le dernier message
        try:
            history = client.conversations_history(
                channel=channel_id,
                limit=1
            )

            if history['messages']:
                last_msg_ts = float(history['messages'][0]['ts'])

                if last_msg_ts < cutoff_ts:
                    days_inactive = int((datetime.now().timestamp() - last_msg_ts) / 86400)
                    inactive.append({
                        'id': channel_id,
                        'name': channel_name,
                        'days_inactive': days_inactive
                    })
            else:
                # Pas de messages du tout
                inactive.append({
                    'id': channel_id,
                    'name': channel_name,
                    'days_inactive': 999
                })

        except SlackApiError as e:
            print(f"Erreur pour #{channel_name}: {e.response['error']}")

    return inactive

def archive_channels(client, channels, dry_run=True):
    """Archive une liste de canaux"""

    for channel in channels:
        if dry_run:
            print(f"[DRY RUN] Archiverait #{channel['name']} ({channel['days_inactive']} jours)")
        else:
            try:
                client.conversations_archive(channel=channel['id'])
                print(f"✅ Archivé #{channel['name']}")
            except SlackApiError as e:
                print(f"❌ Erreur #{channel['name']}: {e.response['error']}")

# Utilisation
if __name__ == '__main__':
    client = WebClient(token="xoxb-YOUR-TOKEN")

    print("🔍 Recherche des canaux inactifs...")
    inactive = find_inactive_channels(client, days=90)

    print(f"\n📊 Trouvé {len(inactive)} canaux inactifs")

    if inactive:
        print("\nCanaux inactifs:")
        for ch in sorted(inactive, key=lambda x: x['days_inactive'], reverse=True):
            print(f"  - #{ch['name']}: {ch['days_inactive']} jours")

        # Archiver (dry run par défaut)
        archive_channels(client, inactive, dry_run=True)
```

### Exemple 3 : Rapport d'audit de sécurité

```python
#!/usr/bin/env python3
"""
Génère un rapport d'audit de sécurité
"""

from slack_sdk import WebClient
import json
from datetime import datetime

def security_audit(client):
    """Génère un rapport d'audit de sécurité"""

    print("🔒 Audit de sécurité en cours...\n")

    # 1. Analyser les utilisateurs
    users = []
    response = client.users_list()
    users = response['members']

    stats = {
        'total': len(users),
        'active': 0,
        'admins': 0,
        'owners': 0,
        'with_2fa': 0,
        'without_2fa': 0,
        'guests': 0
    }

    security_issues = []

    for user in users:
        if user.get('deleted') or user.get('is_bot'):
            continue

        stats['active'] += 1

        if user.get('is_admin'):
            stats['admins'] += 1

        if user.get('is_owner'):
            stats['owners'] += 1

        if user.get('is_restricted') or user.get('is_ultra_restricted'):
            stats['guests'] += 1

        if user.get('has_2fa'):
            stats['with_2fa'] += 1
        else:
            stats['without_2fa'] += 1

            # Issue de sécurité: admin sans 2FA
            if user.get('is_admin') or user.get('is_owner'):
                security_issues.append({
                    'severity': 'HIGH',
                    'type': 'admin_without_2fa',
                    'user': user['name'],
                    'email': user.get('profile', {}).get('email', 'N/A')
                })

    # 2. Analyser les canaux publics
    channels_response = client.conversations_list(types="public_channel")
    public_channels = channels_response['channels']

    # 3. Générer le rapport
    report = {
        'audit_date': datetime.now().isoformat(),
        'workspace_stats': stats,
        'security_issues': security_issues,
        'recommendations': []
    }

    # Recommandations
    if stats['without_2fa'] > 0:
        report['recommendations'].append(
            f"⚠️  {stats['without_2fa']} utilisateurs sans 2FA. "
            "Activer l'obligation de 2FA dans les paramètres."
        )

    if stats['guests'] > stats['active'] * 0.3:
        report['recommendations'].append(
            f"⚠️  Taux élevé d'invités ({stats['guests']}). "
            "Vérifier les permissions des invités."
        )

    # Afficher le rapport
    print("="*60)
    print("RAPPORT D'AUDIT DE SÉCURITÉ")
    print("="*60)
    print(f"\n📊 STATISTIQUES")
    print(f"  Total utilisateurs: {stats['total']}")
    print(f"  Actifs: {stats['active']}")
    print(f"  Administrateurs: {stats['admins']}")
    print(f"  Propriétaires: {stats['owners']}")
    print(f"  Invités: {stats['guests']}")
    print(f"\n🔐 2FA")
    print(f"  Avec 2FA: {stats['with_2fa']} ({stats['with_2fa']/stats['active']*100:.1f}%)")
    print(f"  Sans 2FA: {stats['without_2fa']} ({stats['without_2fa']/stats['active']*100:.1f}%)")

    if security_issues:
        print(f"\n⚠️  PROBLÈMES DE SÉCURITÉ ({len(security_issues)})")
        for issue in security_issues:
            print(f"  [{issue['severity']}] {issue['type']}: {issue['user']} ({issue['email']})")

    if report['recommendations']:
        print(f"\n💡 RECOMMANDATIONS")
        for rec in report['recommendations']:
            print(f"  {rec}")

    # Sauvegarder le rapport
    filename = f"security_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✅ Rapport sauvegardé: {filename}")
    print("="*60)

# Utilisation
if __name__ == '__main__':
    client = WebClient(token="xoxb-YOUR-TOKEN")
    security_audit(client)
```

---

## Debugging

### Activer les logs détaillés

```python
import logging

# Configurer le logging
logging.basicConfig(level=logging.DEBUG)

# Logger du SDK Slack
logger = logging.getLogger('slack_sdk')
logger.setLevel(logging.DEBUG)

# Maintenant toutes les requêtes HTTP seront loggées
client = WebClient(token="xoxb-YOUR-TOKEN")
response = client.users_list()
```

### Inspecter les requêtes

```python
from slack_sdk import WebClient
import json

client = WebClient(token="xoxb-YOUR-TOKEN")

# Faire une requête
response = client.users_info(user="U1234567890")

# Inspecter la réponse complète
print("Status:", response.status_code)
print("Headers:", json.dumps(dict(response.headers), indent=2))
print("Data:", json.dumps(response.data, indent=2))
```

### Tester les permissions

```python
def test_permissions(client):
    """Teste quelles permissions sont disponibles"""

    tests = [
        ('users:read', lambda: client.users_list(limit=1)),
        ('channels:read', lambda: client.conversations_list(limit=1)),
        ('admin.users:read', lambda: client.admin_users_list(limit=1)),
        ('files:read', lambda: client.files_list(count=1)),
    ]

    print("🧪 Test des permissions\n")

    for scope, test_func in tests:
        try:
            test_func()
            print(f"✅ {scope}: OK")
        except SlackApiError as e:
            if e.response['error'] == 'missing_scope':
                print(f"❌ {scope}: MANQUANT")
            else:
                print(f"⚠️  {scope}: {e.response['error']}")

# Utilisation
test_permissions(client)
```

### Outils de développement

```python
class DebugClient:
    """Wrapper pour débugger les appels API"""

    def __init__(self, token):
        self.client = WebClient(token=token)
        self.call_count = 0

    def __getattr__(self, name):
        """Intercepte tous les appels de méthodes"""
        original_method = getattr(self.client, name)

        def wrapper(*args, **kwargs):
            self.call_count += 1
            print(f"\n[Call #{self.call_count}] {name}")
            print(f"  Args: {args}")
            print(f"  Kwargs: {kwargs}")

            try:
                result = original_method(*args, **kwargs)
                print(f"  ✅ Success")
                return result
            except Exception as e:
                print(f"  ❌ Error: {e}")
                raise

        return wrapper

# Utilisation
debug_client = DebugClient(token="xoxb-YOUR-TOKEN")
users = debug_client.users_list(limit=10)
```

---

## Ressources

### Documentation officielle

- **API Slack** : https://api.slack.com/
- **Web API Methods** : https://api.slack.com/methods
- **SDK Python** : https://slack.dev/python-slack-sdk/
- **Block Kit Builder** : https://api.slack.com/block-kit

### Outils utiles

- **Slack API Tester** : https://api.slack.com/methods (bouton "Test Method")
- **Block Kit Builder** : https://app.slack.com/block-kit-builder
- **OAuth Token Generator** : https://api.slack.com/tutorials/tracks/getting-a-token

### Exemples de code

- **GitHub Slack SDK** : https://github.com/slackapi/python-slack-sdk/tree/main/examples
- **Communauté Slack** : https://slackcommunity.com/

### Limites et quotas

- **Rate Limits** : https://api.slack.com/docs/rate-limits
- **Best Practices** : https://api.slack.com/docs/rate-limits#best-practices

---

## Conclusion

L'API Slack est puissante et bien documentée. Les points clés à retenir :

1. **Sécurité** : Ne jamais exposer vos tokens
2. **Permissions** : Utiliser les scopes minimaux nécessaires
3. **Rate Limiting** : Respecter les limites et implémenter des retries
4. **Erreurs** : Gérer proprement toutes les erreurs possibles
5. **Pagination** : Toujours gérer la pagination pour les listes
6. **Tests** : Tester sur un workspace de dev avant production

Bonne automation ! 🚀
