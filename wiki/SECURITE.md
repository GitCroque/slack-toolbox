# 🔒 Guide de Sécurité - Slack Toolbox

> Documentation complète sur les pratiques de sécurité pour l'utilisation et le déploiement de Slack Toolbox

## 📋 Table des matières

1. [Protection des Tokens et Secrets](#-1-protection-des-tokens-et-secrets)
2. [Validation des Entrées](#-2-validation-des-entrées)
3. [Mode Dry-Run](#-3-mode-dry-run)
4. [Bonnes Pratiques](#-4-bonnes-pratiques)
5. [Sécurité CI/CD](#-5-sécurité-cicd)
6. [Gestion des Permissions](#-6-gestion-des-permissions)
7. [Audit de Sécurité](#-7-audit-de-sécurité)
8. [Que faire en cas de Compromission](#-8-que-faire-en-cas-de-compromission)

---

## 🔐 1. Protection des Tokens et Secrets

### 1.1 Stockage Sécurisé

Les tokens Slack sont des informations hautement sensibles qui donnent accès à votre workspace. **Ne les partagez JAMAIS** et ne les commitez **JAMAIS** dans Git.

#### ✅ Check-list de Sécurité des Tokens

- [ ] Les tokens sont stockés dans `config/tokens.conf` (présent dans `.gitignore`)
- [ ] Les permissions du fichier sont restrictives : `chmod 600 config/tokens.conf`
- [ ] Le répertoire config est protégé : `chmod 700 config/`
- [ ] Aucun token n'apparaît dans l'historique Git
- [ ] Les tokens ne sont jamais loggés en clair
- [ ] Utilisation de variables d'environnement en production

#### 📝 Exemple de Configuration Sécurisée

```bash
# Configuration des permissions
chmod 700 config/
chmod 600 config/tokens.conf

# Vérification
ls -la config/tokens.conf
# Devrait afficher : -rw------- (600)
```

#### 🔑 Utilisation avec Variables d'Environnement

```bash
# Définir les tokens via variables d'environnement
export SLACK_TOKEN="xoxb-your-token-here"
export SLACK_USER_TOKEN="xoxp-your-user-token-here"

# Les scripts détecteront automatiquement ces variables
./scripts/archive_old_messages.sh
```

### 1.2 Rotation des Tokens

Effectuez une rotation régulière de vos tokens pour minimiser les risques :

```bash
# 1. Générer un nouveau token sur api.slack.com/apps
# 2. Mettre à jour la configuration
./setup_wizard.py  # Re-configurer avec le nouveau token
# 3. Tester le nouveau token
./slack-manager.py channels list --limit 5
# 4. Révoquer l'ancien token sur api.slack.com
```

**Fréquence recommandée :** Tous les 90 jours minimum, ou immédiatement en cas de suspicion de compromission.

---

## ✔️ 2. Validation des Entrées

### 2.1 Protection contre les Injections

Tous les scripts de Slack Toolbox valident les entrées utilisateur pour prévenir les injections de commandes.

#### 🛡️ Mécanismes de Validation Implémentés

```bash
# Validation des IDs de canaux (format C-xxxxx ou @username)
if [[ ! "$CHANNEL_ID" =~ ^(C[A-Z0-9]{10}|@[a-zA-Z0-9._-]+)$ ]]; then
    echo "❌ Erreur: ID de canal invalide"
    exit 1
fi

# Validation des dates (format ISO)
if ! date -d "$DATE_INPUT" &>/dev/null; then
    echo "❌ Erreur: Format de date invalide"
    exit 1
fi

# Sanitization des noms de fichiers
SAFE_FILENAME=$(echo "$FILENAME" | tr -cd '[:alnum:]._-')
```

### 2.2 Check-list de Validation

Avant d'exécuter un script :

- [ ] Les IDs de canaux sont au bon format (C-xxxxx)
- [ ] Les dates sont valides et au format attendu
- [ ] Les chemins de fichiers ne contiennent pas de caractères dangereux (`..`, `;`, `|`)
- [ ] Les limites numériques sont dans des plages acceptables
- [ ] Les patterns de recherche ne contiennent pas de regex malveillantes

---

## 🧪 3. Mode Dry-Run

Le mode dry-run permet de simuler les opérations sans effectuer de modifications réelles.

### 3.1 Utilisation du Mode Dry-Run

```bash
# Archive avec simulation
./scripts/archive_old_messages.sh --dry-run

# Nettoyage de fichiers avec simulation
./scripts/cleanup_old_files.sh --dry-run

# Toute opération destructive devrait être testée d'abord
DRY_RUN=true ./scripts/delete_messages.sh --channel C123456
```

### 3.2 Bonnes Pratiques avec Dry-Run

#### ✅ Workflow Recommandé

```bash
# 1. D'abord en mode dry-run
./scripts/cleanup_old_files.sh --dry-run --days 180

# 2. Analyser la sortie
# Vérifier les fichiers qui seraient supprimés

# 3. Si tout est correct, exécution réelle
./scripts/cleanup_old_files.sh --days 180

# 4. Vérifier les logs
tail -f logs/cleanup_old_files.log
```

#### 🎯 Avantages du Dry-Run

- ✅ Prévient les suppressions accidentelles
- ✅ Permet de vérifier la logique avant exécution
- ✅ Identifie les erreurs potentielles sans risque
- ✅ Facilite les tests et la validation
- ✅ Génère des rapports prévisionnels

---

## 🎯 4. Bonnes Pratiques

### 4.1 Principe du Moindre Privilège

#### 🔐 Tokens et Scopes

Utilisez uniquement les scopes nécessaires pour chaque tâche :

```yaml
# Bot Token (xoxb-) - Scopes recommandés minimum
channels:read     # Lister les canaux
channels:history  # Lire l'historique
files:read        # Lire les fichiers
users:read        # Informations utilisateurs

# User Token (xoxp-) - Uniquement si nécessaire
channels:write    # Archiver des canaux (nécessite user token)
```

#### 👤 Permissions Fichiers

```bash
# Scripts exécutables : 750 (rwxr-x---)
chmod 750 scripts/*.sh

# Fichiers de configuration : 600 (rw-------)
chmod 600 config/*.conf

# Logs : 640 (rw-r-----)
chmod 640 logs/*.log

# Répertoires : 750 (rwxr-x---)
chmod 750 config/ logs/ scripts/
```

### 4.2 Surveillance et Logging

#### 📊 Check-list de Monitoring

- [ ] Tous les scripts loggent dans `logs/`
- [ ] Rotation des logs configurée (logrotate)
- [ ] Alertes configurées pour les opérations critiques
- [ ] Revue régulière des logs d'erreurs
- [ ] Monitoring des taux d'erreur API

#### 📝 Exemple de Configuration de Logs

```bash
# Configuration logrotate pour /etc/logrotate.d/slack-toolbox
/home/user/slack-toolbox/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 640 user user
    sharedscripts
}
```

### 4.3 Sauvegardes

```bash
# Sauvegarde avant opération critique
./scripts/backup_channel_data.sh --channel C123456 --output backups/

# Vérification de la sauvegarde
ls -lh backups/
tar -tzf backups/channel_C123456_*.tar.gz
```

---

## 🔄 5. Sécurité CI/CD

### 5.1 Secrets dans GitHub Actions

#### ⚙️ Configuration Sécurisée

```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Bandit Security Scan
        run: |
          pip install bandit
          bandit -r scripts/ -f json -o bandit-report.json

      - name: Check for secrets
        run: |
          pip install detect-secrets
          detect-secrets scan --baseline .secrets.baseline
```

#### 🔑 Gestion des Secrets GitHub

```bash
# Ajouter des secrets via GitHub CLI
gh secret set SLACK_TOKEN --body "xoxb-your-token"
gh secret set SLACK_USER_TOKEN --body "xoxp-your-token"

# Liste des secrets (valeurs masquées)
gh secret list
```

### 5.2 Protection des Branches

#### ✅ Configuration Recommandée

- [ ] Branch protection sur `main` et `master`
- [ ] Require pull request reviews (minimum 1 reviewer)
- [ ] Require status checks to pass (tests, security scans)
- [ ] Require branches to be up to date
- [ ] Include administrators (pas d'exception)

### 5.3 Scan de Vulnérabilités

```bash
# Scan avec Bandit
bandit -r scripts/ lib/ -ll

# Scan avec Safety (dépendances Python)
safety check -r requirements.txt

# Scan pre-commit hooks
pre-commit run --all-files bandit
pre-commit run --all-files detect-secrets
```

---

## 👥 6. Gestion des Permissions

### 6.1 Niveaux d'Accès

#### 🎭 Rôles et Responsabilités

| Rôle | Accès | Responsabilités |
|------|-------|-----------------|
| **Admin** | Complet | Installation, configuration tokens, operations critiques |
| **Opérateur** | Scripts de monitoring et reporting | Exécution quotidienne, analyse des données |
| **Auditeur** | Lecture seule (logs, rapports) | Revue de sécurité, compliance |

### 6.2 Séparation des Environnements

```bash
# config/tokens.conf.production
SLACK_TOKEN="xoxb-production-token"

# config/tokens.conf.staging
SLACK_TOKEN="xoxb-staging-token"

# config/tokens.conf.development
SLACK_TOKEN="xoxb-development-token"

# Charger l'environnement approprié
source config/tokens.conf.$ENVIRONMENT
```

### 6.3 Audit des Accès

```bash
# Vérifier qui a accès aux tokens
ls -l config/tokens.conf

# Historique des modifications
git log --follow -- config/tokens.conf

# Logs des connexions Slack
grep "API call" logs/*.log | tail -50
```

---

## 🔍 7. Audit de Sécurité

### 7.1 Check-list d'Audit Mensuel

- [ ] Revue des logs d'accès et d'erreurs
- [ ] Vérification des permissions fichiers
- [ ] Scan de vulnérabilités (Bandit, Safety)
- [ ] Test des sauvegardes
- [ ] Validation de la rotation des logs
- [ ] Revue des scopes de tokens
- [ ] Vérification .gitignore (pas de secrets commités)
- [ ] Test des alertes et monitoring
- [ ] Mise à jour des dépendances

### 7.2 Commandes d'Audit

```bash
# Audit complet automatisé
make security-audit

# Vérification manuelle
./scripts/security_check.sh

# Rapport de sécurité
./scripts/generate_security_report.sh --output reports/security_$(date +%Y%m%d).pdf
```

### 7.3 Tests de Sécurité

```bash
# Tests unitaires avec couverture de sécurité
pytest tests/ --cov=scripts --cov-report=html

# Tests d'intégration
pytest tests/integration/ -v

# Tests de pénétration (environnement de test uniquement)
./tests/security/penetration_tests.sh
```

---

## 🚨 8. Que faire en cas de Compromission

### 8.1 Réponse Immédiate (1ère heure)

#### ⚡ Actions Urgentes

1. **Révoquer immédiatement tous les tokens**
   ```bash
   # Sur api.slack.com/apps → Votre App → OAuth & Permissions
   # Cliquez sur "Revoke" pour tous les tokens
   ```

2. **Désactiver les cron jobs**
   ```bash
   crontab -e
   # Commenter toutes les lignes
   # Sauvegarder
   ```

3. **Isoler le système compromis**
   ```bash
   # Bloquer l'accès réseau si possible
   sudo iptables -A OUTPUT -j DROP
   ```

4. **Notifier l'équipe de sécurité**
   - Email à security@votre-entreprise.com
   - Slack #security-incidents
   - Manager direct

### 8.2 Investigation (24 heures)

```bash
# Collecter les preuves
mkdir /tmp/incident_$(date +%Y%m%d_%H%M%S)
cd /tmp/incident_*

# Copier les logs
cp -r /home/user/slack-toolbox/logs/ ./

# Historique des commandes
history > command_history.txt

# Connexions réseau actives
netstat -tuln > network_connections.txt

# Processus en cours
ps aux > running_processes.txt

# Dernières modifications de fichiers
find /home/user/slack-toolbox -type f -mtime -7 -ls > recent_changes.txt
```

### 8.3 Remédiation

#### ✅ Check-list de Récupération

- [ ] Identifier la source de la compromission
- [ ] Générer de nouveaux tokens avec scopes minimaux
- [ ] Changer tous les mots de passe associés
- [ ] Re-déployer depuis une source propre (Git)
- [ ] Mettre à jour toutes les dépendances
- [ ] Vérifier l'intégrité des fichiers (`sha256sum`)
- [ ] Re-configurer avec `./setup_wizard.py`
- [ ] Activer l'authentification 2FA sur Slack
- [ ] Revoir les permissions d'accès
- [ ] Réactiver les cron jobs après validation

### 8.4 Post-Mortem

```bash
# Template de rapport d'incident
cat > incident_report_$(date +%Y%m%d).md << 'EOF'
# Rapport d'Incident de Sécurité

## Résumé
- **Date:**
- **Détecteur:**
- **Sévérité:** [Critique/Haute/Moyenne/Basse]

## Chronologie
- **HH:MM** - Détection de l'incident
- **HH:MM** - Révocation des tokens
- **HH:MM** - Investigation démarrée
- **HH:MM** - Résolution

## Impact
- Tokens compromis: [Oui/Non]
- Données exposées: [Description]
- Services affectés: [Liste]

## Cause Racine
[Description détaillée]

## Actions Correctives
- [ ] Action 1
- [ ] Action 2

## Leçons Apprises
[Ce qu'on a appris pour prévenir de futurs incidents]
EOF
```

---

## 📞 Contacts et Ressources

### 🆘 Support d'Urgence

- **Slack Security:** <https://slack.com/help/articles/360000291563>
- **GitHub Security:** <https://github.com/security>
- **Repository Issues:** <https://github.com/votre-org/slack-toolbox/issues>

### 📚 Documentation Complémentaire

- [ARCHITECTURE.md](/ARCHITECTURE.md) - Architecture de sécurité
- [CONTRIBUTING.md](/CONTRIBUTING.md) - Guidelines de développement sécurisé
- [SLACK_API_GUIDE.md](/SLACK_API_GUIDE.md) - Sécurité de l'API Slack

---

## 🔄 Historique des Révisions

| Version | Date | Modifications |
|---------|------|---------------|
| 1.0 | 2025-11-17 | Création du document |

---

**⚠️ Important:** Ce document doit être revu et mis à jour régulièrement. Toute modification des pratiques de sécurité doit être documentée ici.

**🔒 Statut:** Document vivant - Dernière mise à jour: 2025-11-17
