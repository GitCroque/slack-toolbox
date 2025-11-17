# ❓ FAQ - Questions Fréquentes

> Réponses aux questions les plus courantes sur Slack Toolbox

---

## 📋 Table des matières

1. [Questions générales](#-1-questions-générales)
2. [Installation](#-2-installation)
3. [Configuration](#-3-configuration)
4. [Utilisation](#-4-utilisation)
5. [Problèmes courants](#-5-problèmes-courants)
6. [Performance](#-6-performance)
7. [Sécurité](#-7-sécurité)
8. [Développement](#-8-développement)

---

## 🌟 1. Questions générales

### Q: Qu'est-ce que Slack Toolbox ?

**R:** Slack Toolbox est une suite professionnelle d'outils CLI pour gérer votre espace de travail Slack. Elle permet de :
- 👥 Gérer les utilisateurs (inviter, désactiver, exporter)
- 💬 Administrer les canaux (créer, archiver, auditer)
- 🔍 Effectuer des audits de sécurité et conformité
- 💾 Créer des sauvegardes complètes
- 📊 Générer des rapports et statistiques détaillés

### Q: Pourquoi utiliser Slack Toolbox plutôt que l'interface web Slack ?

**R:** Plusieurs avantages :
- ⚡ **Automatisation** : Scripter les tâches répétitives
- 🔄 **Batch Operations** : Traiter des centaines d'utilisateurs/canaux en masse
- 💾 **Sauvegarde** : Exporter l'historique complet impossible via l'interface
- 📊 **Rapports avancés** : Statistiques détaillées et analyses
- 🔍 **Audit** : Détection automatique des problèmes de sécurité
- 🎯 **CI/CD** : Intégration dans vos pipelines DevOps

### Q: Quels sont les prérequis pour utiliser Slack Toolbox ?

**R:**
- Python 3.8+ installé
- Un compte Slack avec droits d'administration
- Un token d'API Slack avec les scopes appropriés
- Connexion Internet stable

### Q: Est-ce que Slack Toolbox est gratuit ?

**R:** Oui, Slack Toolbox est 100% gratuit et open-source sous licence MIT. Vous pouvez l'utiliser, le modifier et le redistribuer librement.

### Q: Slack Toolbox fonctionne-t-il avec Slack gratuit ?

**R:** Oui, mais avec des limitations :
- ✅ Gestion des utilisateurs et canaux
- ✅ Exports basiques
- ❌ Historique complet limité à 90 jours (limitation Slack)
- ❌ Certaines fonctionnalités d'audit nécessitent Slack Plus/Enterprise

### Q: Combien d'utilisateurs/canaux puis-je gérer ?

**R:** Aucune limite côté Slack Toolbox. Testé avec succès sur des workspaces de :
- 👥 10,000+ utilisateurs
- 💬 5,000+ canaux
- 📦 100+ GB de données exportées

---

## 🔧 2. Installation

### Q: Quelle version de Python est requise ?

**R:** Python **3.8 ou supérieur**. Vérifiez votre version :

```bash
python3 --version
# Output: Python 3.8.x ou plus récent
```

Si vous avez une version antérieure, installez Python 3.8+ :

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3.8

# macOS (via Homebrew)
brew install python@3.8

# Windows
# Télécharger depuis python.org
```

### Q: L'installation échoue avec "ModuleNotFoundError" ?

**R:** Cela signifie que les dépendances ne sont pas installées. Solutions :

**Solution 1 : Utiliser le setup wizard (recommandé)**
```bash
python3 setup_wizard.py
# Installe automatiquement toutes les dépendances
```

**Solution 2 : Installation manuelle**
```bash
pip install -r requirements.txt
```

**Solution 3 : Environnement virtuel**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Q: Erreur "Permission denied" lors de l'installation ?

**R:** Vous n'avez pas les droits nécessaires. Solutions :

```bash
# Option 1 : Installation utilisateur (recommandé)
pip install --user -r requirements.txt

# Option 2 : Utiliser sudo (Linux/Mac seulement)
sudo pip install -r requirements.txt

# Option 3 : Environnement virtuel (meilleure pratique)
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### Q: Comment vérifier que l'installation est réussie ?

**R:** Lancez les tests :

```bash
# Test rapide
python slack-manager.py --version

# Tests complets
make test
# Devrait afficher : 213 tests passés

# Vérifier les dépendances
pip list | grep slack
```

### Q: L'installation fonctionne mais les scripts ne trouvent pas les modules ?

**R:** Problème de PYTHONPATH. Solutions :

```bash
# Solution 1 : Ajouter au PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/home/user/slack-toolbox"

# Solution 2 : Lancer depuis le bon répertoire
cd /home/user/slack-toolbox
python slack-manager.py

# Solution 3 : Ajouter à ~/.bashrc (permanent)
echo 'export PYTHONPATH="${PYTHONPATH}:/chemin/vers/slack-toolbox"' >> ~/.bashrc
```

### Q: Quelles sont les dépendances principales ?

**R:** Les packages essentiels :
- `slack-sdk` : SDK officiel Slack
- `python-dotenv` : Gestion des variables d'environnement
- `requests` : Requêtes HTTP
- `pandas` : Manipulation de données (pour les exports CSV/Excel)
- `pytest` : Framework de tests

---

## ⚙️ 3. Configuration

### Q: Comment obtenir un token Slack ?

**R:** Suivez ces étapes :

1. **Aller sur https://api.slack.com/apps**
2. **Créer une nouvelle app** : "Create New App" → "From scratch"
3. **Nommer votre app** : Ex: "Slack Toolbox"
4. **Sélectionner votre workspace**
5. **Ajouter les scopes OAuth** dans "OAuth & Permissions" :
   ```
   users:read, users:write, channels:read, channels:write,
   channels:manage, chat:write, files:read, admin.users:read,
   admin.users:write, admin.conversations:read
   ```
6. **Installer l'app** dans votre workspace
7. **Copier le "Bot User OAuth Token"** (commence par `xoxb-`)

### Q: Quelles permissions (scopes) sont nécessaires ?

**R:** Dépend de vos besoins :

**Minimum (lecture seule) :**
```
users:read
channels:read
```

**Gestion basique :**
```
users:read
users:write
channels:read
channels:write
channels:manage
chat:write
```

**Complet (toutes fonctionnalités) :**
```
users:read, users:write
channels:read, channels:write, channels:manage
chat:write, files:read, files:write
admin.users:read, admin.users:write
admin.conversations:read, admin.conversations:write
groups:read, groups:write, mpim:read, im:read
```

Voir [wiki/CONFIGURATION.md](./CONFIGURATION.md) pour la liste complète.

### Q: Erreur "missing_scope" lors de l'utilisation ?

**R:** Votre token n'a pas les permissions nécessaires :

1. **Identifier le scope manquant** dans l'erreur :
   ```
   Error: missing_scope: Need channels:write
   ```

2. **Ajouter le scope** :
   - Aller sur https://api.slack.com/apps
   - Sélectionner votre app
   - "OAuth & Permissions" → "Scopes"
   - Ajouter le scope manquant
   - **Réinstaller l'app** (important !)

3. **Copier le nouveau token** et mettre à jour `.env`

### Q: Comment configurer le fichier .env ?

**R:** Créez un fichier `.env` à la racine :

```bash
# Token Slack (OBLIGATOIRE)
SLACK_BOT_TOKEN=xoxb-votre-token-ici

# Configuration optionnelle
SLACK_WORKSPACE_ID=T01234567
DRY_RUN=false
LOG_LEVEL=INFO
RATE_LIMIT_DELAY=1.0

# Webhooks (optionnel)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ

# Export paths
EXPORT_DIR=/chemin/vers/exports
BACKUP_DIR=/chemin/vers/backups
```

**Astuce** : Utilisez le setup wizard qui crée automatiquement `.env` :
```bash
python3 setup_wizard.py
```

### Q: Comment tester si la configuration fonctionne ?

**R:** Plusieurs méthodes :

```bash
# Test 1 : Lister les utilisateurs (lecture seule)
python scripts/user_manager.py --list

# Test 2 : Test de connexion
python -c "from utils.slack_api import SlackAPI; api = SlackAPI(); print(api.test_connection())"

# Test 3 : Dry-run (sans modification)
python slack-manager.py --dry-run

# Test 4 : Lancer les tests
make test
```

### Q: Peut-on utiliser plusieurs tokens pour différents workspaces ?

**R:** Oui ! Deux approches :

**Approche 1 : Fichiers .env multiples**
```bash
# .env.workspace1
SLACK_BOT_TOKEN=xoxb-token-workspace1

# .env.workspace2
SLACK_BOT_TOKEN=xoxb-token-workspace2

# Utilisation
export ENV_FILE=.env.workspace1
python slack-manager.py
```

**Approche 2 : Variable d'environnement**
```bash
SLACK_BOT_TOKEN=xoxb-workspace1 python slack-manager.py
```

---

## 🎮 4. Utilisation

### Q: Comment utiliser le mode dry-run ?

**R:** Le mode dry-run simule les actions sans les exécuter. Toujours recommandé pour tester !

```bash
# Méthode 1 : Flag --dry-run
python slack-manager.py --dry-run

# Méthode 2 : Variable d'environnement
export DRY_RUN=true
python slack-manager.py

# Méthode 3 : Dans .env
DRY_RUN=true

# Exemple : Tester l'archivage sans vraiment archiver
python scripts/channel_manager.py --archive-inactive --days 90 --dry-run
```

### Q: Comment lister tous les utilisateurs ?

**R:** Plusieurs options :

```bash
# Option 1 : CLI interactif
python slack-manager.py
# Puis choisir : 1 (User Management) → 1 (List users)

# Option 2 : Script direct
python scripts/user_manager.py --list

# Option 3 : Makefile
make list-users

# Option 4 : Avec export CSV
python scripts/user_manager.py --list --export users.csv
```

### Q: Comment inviter des utilisateurs en masse ?

**R:** Créez un fichier CSV puis utilisez le script d'invitation :

**1. Créer `invites.csv` :**
```csv
email,first_name,last_name,channels
john@example.com,John,Doe,"general,dev"
jane@example.com,Jane,Smith,"general,marketing"
```

**2. Lancer l'invitation :**
```bash
# Test d'abord en dry-run
python scripts/user_manager.py --invite invites.csv --dry-run

# Ensuite vraiment inviter
python scripts/user_manager.py --invite invites.csv

# Ou via Makefile
make invite-users FILE=invites.csv
```

### Q: Comment exporter l'historique des messages ?

**R:** Utilisez le script de sauvegarde :

```bash
# Export complet
python scripts/backup_manager.py --full-backup

# Export d'un canal spécifique
python scripts/backup_manager.py --channel general --output general_backup.json

# Export période spécifique
python scripts/backup_manager.py --channel general --start 2024-01-01 --end 2024-12-31

# Formats disponibles : JSON, CSV, HTML
python scripts/backup_manager.py --channel general --format html
```

### Q: Comment archiver les canaux inactifs ?

**R:** Le script détecte et archive automatiquement :

```bash
# Lister les canaux inactifs (sans archiver)
python scripts/channel_manager.py --list-inactive --days 90

# Archiver en dry-run (recommandé d'abord)
python scripts/channel_manager.py --archive-inactive --days 90 --dry-run

# Vraiment archiver
python scripts/channel_manager.py --archive-inactive --days 90

# Avec confirmation pour chaque canal
python scripts/channel_manager.py --archive-inactive --days 90 --interactive
```

### Q: Comment générer des rapports ?

**R:** Plusieurs types de rapports disponibles :

```bash
# Rapport utilisateurs
python scripts/reporting.py --user-stats --output reports/users.pdf

# Rapport canaux
python scripts/reporting.py --channel-stats --output reports/channels.pdf

# Rapport d'activité
python scripts/reporting.py --activity --days 30 --output reports/activity.html

# Dashboard complet
python scripts/reporting.py --dashboard --output reports/dashboard.html

# Via Makefile
make reports
```

---

## 🚨 5. Problèmes courants

### Q: Erreur "rate_limited" - Que faire ?

**R:** Slack limite le nombre de requêtes API. Solutions :

**Solution 1 : Augmenter le délai (recommandé)**
```python
# Dans .env
RATE_LIMIT_DELAY=2.0  # Secondes entre chaque requête
```

**Solution 2 : Utiliser le mode batch**
```bash
# Au lieu de multiples appels
python scripts/user_manager.py --list --limit 100
```

**Solution 3 : Attendre et réessayer**
```bash
# L'erreur indique combien de temps attendre
# Exemple : "Retry after 60 seconds"
sleep 60 && python slack-manager.py
```

**Configuration recommandée pour gros workspaces :**
```bash
RATE_LIMIT_DELAY=1.5
BATCH_SIZE=50
MAX_RETRIES=3
```

### Q: Erreur "token_revoked" ou "invalid_auth" ?

**R:** Votre token n'est plus valide :

1. **Vérifier le token dans .env** (pas d'espaces, complet)
2. **Régénérer un nouveau token** :
   - https://api.slack.com/apps
   - Sélectionner votre app
   - "OAuth & Permissions" → "Reinstall App"
3. **Mettre à jour .env** avec le nouveau token
4. **Tester** :
   ```bash
   python -c "from utils.slack_api import SlackAPI; print(SlackAPI().test_connection())"
   ```

### Q: Erreur "channel_not_found" ?

**R:** Le canal n'existe pas ou le bot n'y a pas accès :

```bash
# Vérifier que le canal existe
python scripts/channel_manager.py --list | grep "nom-canal"

# Inviter le bot au canal (dans Slack)
/invite @VotreBot

# Utiliser l'ID du canal au lieu du nom
python scripts/channel_manager.py --channel C01234567 --info
```

### Q: Erreur "users_not_found" lors des invitations ?

**R:** Plusieurs causes possibles :

1. **Email invalide** : Vérifier le format
   ```csv
   # ❌ Incorrect
   john@exemple,com

   # ✅ Correct
   john@exemple.com
   ```

2. **Utilisateur déjà membre** : Normal, ignoré automatiquement

3. **Workspace avec restrictions** : Vérifier les paramètres Slack

4. **Utiliser le mode verbose** pour déboguer :
   ```bash
   python scripts/user_manager.py --invite invites.csv --verbose
   ```

### Q: Les exports sont vides ou incomplets ?

**R:** Vérifications :

1. **Permissions insuffisantes** : Ajouter scopes `files:read` et `channels:history`

2. **Limite temporelle** : Slack gratuit = 90 jours seulement
   ```bash
   # Vérifier la période disponible
   python scripts/backup_manager.py --check-limits
   ```

3. **Canal privé** : Le bot doit être membre
   ```bash
   # Lister les canaux accessibles
   python scripts/channel_manager.py --list --accessible-only
   ```

4. **Trop de messages** : Utiliser la pagination
   ```bash
   python scripts/backup_manager.py --channel general --max-messages 10000
   ```

### Q: Script bloqué / ne répond plus ?

**R:** Causes courantes :

1. **Rate limiting** : Normal sur gros workspaces
   ```bash
   # Suivre la progression avec verbose
   python slack-manager.py --verbose
   ```

2. **Timeout réseau** : Augmenter le timeout
   ```python
   # Dans .env
   REQUEST_TIMEOUT=60
   ```

3. **Trop de données** : Traiter par lots
   ```bash
   # Au lieu d'exporter tout
   python scripts/backup_manager.py --channels general,random --limit 1000
   ```

---

## ⚡ 6. Performance

### Q: Comment optimiser les performances pour un gros workspace ?

**R:** Plusieurs techniques :

**1. Batch Processing**
```python
# Dans .env
BATCH_SIZE=100          # Traiter 100 items à la fois
CONCURRENT_REQUESTS=5   # 5 requêtes en parallèle (prudent !)
```

**2. Caching**
```bash
# Activer le cache (réduit les appels API)
ENABLE_CACHE=true
CACHE_TTL=3600  # 1 heure
```

**3. Filtrage**
```bash
# Exporter seulement ce dont vous avez besoin
python scripts/backup_manager.py --channels general,dev --days 30
# Au lieu de --all-channels
```

**4. Compression**
```bash
# Compresser les exports
python scripts/backup_manager.py --compress --format json.gz
```

### Q: Combien de temps prend un export complet ?

**R:** Dépend de la taille :

| Workspace | Utilisateurs | Canaux | Messages | Temps estimé |
|-----------|--------------|--------|----------|--------------|
| Petit | < 50 | < 20 | < 10k | 1-5 min |
| Moyen | 50-500 | 20-100 | 10k-100k | 10-30 min |
| Grand | 500-5000 | 100-500 | 100k-1M | 1-3 heures |
| Entreprise | 5000+ | 500+ | 1M+ | 3-12 heures |

**Astuce** : Utiliser `--progress` pour suivre l'avancement :
```bash
python scripts/backup_manager.py --full-backup --progress
```

### Q: Comment réduire l'utilisation mémoire ?

**R:** Techniques :

**1. Streaming au lieu de charger tout en mémoire**
```bash
# Utiliser --stream pour gros exports
python scripts/backup_manager.py --channel general --stream --output messages.jsonl
```

**2. Limiter la taille des lots**
```python
# Dans .env
BATCH_SIZE=50     # Au lieu de 200
MAX_MESSAGES=1000 # Limiter par canal
```

**3. Nettoyer les caches**
```bash
# Nettoyer après chaque export
python scripts/cleanup.py --clear-cache
```

### Q: Le rate limiting ralentit trop les opérations ?

**R:** Équilibre entre vitesse et respect des limites :

**Configuration agressive (risque rate limit) :**
```bash
RATE_LIMIT_DELAY=0.5
CONCURRENT_REQUESTS=3
```

**Configuration équilibrée (recommandé) :**
```bash
RATE_LIMIT_DELAY=1.0
CONCURRENT_REQUESTS=2
MAX_RETRIES=3
```

**Configuration prudente (workspaces avec restrictions) :**
```bash
RATE_LIMIT_DELAY=2.0
CONCURRENT_REQUESTS=1
MAX_RETRIES=5
```

---

## 🔐 7. Sécurité

### Q: Mon token a été compromis, que faire ?

**R:** Action immédiate !

**1. Révoquer le token (URGENT)**
```bash
# Aller sur https://api.slack.com/apps
# OAuth & Permissions → Revoke Token
```

**2. Supprimer des fichiers**
```bash
# Supprimer .env
rm .env

# Supprimer des logs (peuvent contenir le token)
rm -rf logs/
find . -name "*.log" -delete

# Vérifier git history
git log --all -- .env
```

**3. Générer un nouveau token**
- Recréer l'app Slack
- Ajouter les scopes nécessaires
- Réinstaller dans le workspace

**4. Mettre à jour .gitignore**
```bash
# S'assurer que .env est ignoré
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Security: Ensure .env is gitignored"
```

### Q: Comment sécuriser les tokens ?

**R:** Meilleures pratiques :

**1. Fichier .env avec permissions restrictives**
```bash
# Créer .env
touch .env
chmod 600 .env  # Lecture/écriture propriétaire seulement

# Ajouter token
echo "SLACK_BOT_TOKEN=xoxb-your-token" >> .env
```

**2. Ne JAMAIS commiter .env**
```bash
# Vérifier .gitignore
cat .gitignore | grep .env

# Si absent, ajouter
echo -e "\n# Environment variables\n.env\n.env.*" >> .gitignore
```

**3. Utiliser un gestionnaire de secrets (production)**
```bash
# Exemple avec AWS Secrets Manager
aws secretsmanager create-secret --name slack-token --secret-string "xoxb-..."

# Ou HashiCorp Vault
vault kv put secret/slack token=xoxb-...
```

**4. Rotation régulière des tokens**
- Renouveler tous les 90 jours minimum
- Automatiser avec un script

### Q: Les logs peuvent-ils exposer des informations sensibles ?

**R:** Par défaut, non. Slack Toolbox masque les tokens :

```python
# Les tokens sont automatiquement masqués dans les logs
# Token réel : xoxb-1234567890-1234567890-abcdefghijk
# Dans les logs : xoxb-****-****-****
```

**Configuration sécurisée des logs :**
```python
# Dans .env
LOG_LEVEL=INFO          # Pas DEBUG en production
MASK_SENSITIVE_DATA=true
LOG_FILE=/secure/path/app.log

# Permissions restrictives
chmod 600 /secure/path/app.log
```

### Q: Comment auditer les permissions actuelles ?

**R:** Script d'audit intégré :

```bash
# Audit complet
python scripts/security_audit.py --full-report

# Vérifier les permissions du bot
python scripts/security_audit.py --check-scopes

# Détecter les tokens expirés
python scripts/security_audit.py --check-tokens

# Rapport de sécurité PDF
python scripts/security_audit.py --output security-report.pdf
```

### Q: Comment limiter l'accès aux scripts ?

**R:** Contrôle d'accès :

```bash
# 1. Permissions fichiers
chmod 700 scripts/*.py  # Exécution propriétaire seulement
chmod 600 .env          # Lecture propriétaire seulement

# 2. Utiliser des rôles UNIX
sudo chown slack-admin:slack-admin slack-toolbox/
sudo chmod 770 slack-toolbox/

# 3. Logs d'audit
AUDIT_LOG=true  # Dans .env
# Trace qui exécute quoi
```

---

## 💻 8. Développement

### Q: Comment contribuer au projet ?

**R:** Processus simple :

**1. Fork et clone**
```bash
# Fork sur GitHub, puis
git clone https://github.com/VOTRE-USERNAME/slack-toolbox.git
cd slack-toolbox
```

**2. Créer une branche**
```bash
git checkout -b feature/ma-fonctionnalite
```

**3. Développer avec les standards**
```bash
# Installer dev dependencies
pip install -r requirements-dev.txt

# Lancer les tests
make test

# Vérifier le style (PEP 8)
make lint

# Formatter le code
make format
```

**4. Commit et PR**
```bash
# Commit avec message clair
git add .
git commit -m "Add: Description de la fonctionnalité"

# Push et créer PR
git push origin feature/ma-fonctionnalite
# Puis créer PR sur GitHub
```

### Q: Comment lancer les tests ?

**R:** Plusieurs niveaux de tests :

```bash
# Tous les tests
make test

# Tests avec couverture
make test-coverage

# Tests d'un module spécifique
pytest tests/test_user_manager.py

# Tests avec verbose
pytest -v

# Tests en parallèle (plus rapide)
pytest -n auto

# Tests d'intégration seulement
pytest tests/integration/
```

### Q: Quels sont les standards de code ?

**R:** Nous suivons :

**1. PEP 8** (style Python)
```bash
# Vérifier
flake8 scripts/ utils/

# Auto-formatter
black scripts/ utils/
```

**2. Type hints** (Python 3.8+)
```python
# ✅ Bon
def get_user(user_id: str) -> Dict[str, Any]:
    pass

# ❌ Éviter
def get_user(user_id):
    pass
```

**3. Docstrings** (Google style)
```python
def invite_users(emails: List[str], channels: List[str]) -> Dict:
    """Invite multiple users to specified channels.

    Args:
        emails: List of email addresses to invite
        channels: List of channel IDs to add users to

    Returns:
        Dict with results: {'success': [...], 'failed': [...]}

    Raises:
        SlackAPIError: If API call fails
    """
    pass
```

**4. Tests**
- Couverture minimale : 80%
- Tests unitaires pour chaque fonction
- Tests d'intégration pour workflows complets

### Q: Comment déboguer un problème ?

**R:** Approche systématique :

**1. Activer le mode verbose**
```bash
# Dans .env
LOG_LEVEL=DEBUG
VERBOSE=true

# Ou en ligne de commande
python slack-manager.py --verbose --debug
```

**2. Lire les logs**
```bash
# Logs récents
tail -f logs/slack-toolbox.log

# Chercher les erreurs
grep -i "error" logs/slack-toolbox.log

# Logs d'une date spécifique
grep "2024-11-17" logs/slack-toolbox.log
```

**3. Python debugger**
```python
# Ajouter un breakpoint
import pdb; pdb.set_trace()

# Ou utiliser breakpoint() (Python 3.7+)
breakpoint()
```

**4. Tests interactifs**
```bash
# Lancer Python REPL
python3
>>> from utils.slack_api import SlackAPI
>>> api = SlackAPI()
>>> api.list_users()
```

### Q: Comment ajouter une nouvelle fonctionnalité ?

**R:** Template à suivre :

**1. Créer le script**
```python
# scripts/ma_fonctionnalite.py
"""
Module de description.
"""

from utils.slack_api import SlackAPI
from typing import List, Dict

def ma_fonction(param: str) -> Dict:
    """Docstring claire."""
    api = SlackAPI()
    # Implémentation
    return result

if __name__ == "__main__":
    # CLI arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--param", required=True)
    args = parser.parse_args()

    result = ma_fonction(args.param)
    print(result)
```

**2. Ajouter les tests**
```python
# tests/test_ma_fonctionnalite.py
import pytest
from scripts.ma_fonctionnalite import ma_fonction

def test_ma_fonction():
    result = ma_fonction("test")
    assert result is not None
    assert "expected_key" in result
```

**3. Mettre à jour la documentation**
```markdown
# wiki/UTILISATION.md
## Ma fonctionnalité

Description...

\`\`\`bash
python scripts/ma_fonctionnalite.py --param valeur
\`\`\`
```

**4. Ajouter au Makefile** (optionnel)
```makefile
.PHONY: ma-commande
ma-commande:
	python scripts/ma_fonctionnalite.py --param $(PARAM)
```

### Q: Comment publier une release ?

**R:** Processus (mainteneurs seulement) :

```bash
# 1. Vérifier que tout passe
make test && make lint

# 2. Mettre à jour VERSION
echo "1.2.0" > VERSION

# 3. Mettre à jour CHANGELOG.md
# Ajouter les nouveautés

# 4. Commit et tag
git add VERSION CHANGELOG.md
git commit -m "Release: v1.2.0"
git tag -a v1.2.0 -m "Version 1.2.0"

# 5. Push
git push origin main --tags

# 6. GitHub Release
gh release create v1.2.0 --notes "Release notes..."
```

---

## 📞 Support

Vous ne trouvez pas la réponse à votre question ?

- 📖 **Documentation complète** : [Wiki](./README.md)
- 🐛 **Signaler un bug** : [GitHub Issues](https://github.com/GitCroque/slack-toolbox/issues)
- 💬 **Discussions** : [GitHub Discussions](https://github.com/GitCroque/slack-toolbox/discussions)
- 📧 **Contact** : gitcroque@example.com

---

**Dernière mise à jour** : 2025-11-17
