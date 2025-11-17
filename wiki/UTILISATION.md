# 📖 Guide d'Utilisation - Slack Toolbox

> Guide complet pour maîtriser toutes les fonctionnalités de Slack Toolbox

---

## 📋 Table des matières

1. [Démarrage](#-1-démarrage)
2. [Gestion des utilisateurs](#-2-gestion-des-utilisateurs)
3. [Gestion des canaux](#-3-gestion-des-canaux)
4. [Audit et conformité](#-4-audit-et-conformité)
5. [Sauvegardes](#-5-sauvegardes)
6. [Monitoring et alertes](#-6-monitoring-et-alertes)
7. [Exemples pratiques](#-7-exemples-pratiques)

---

## 🚀 1. Démarrage

### 1.1 CLI Interactif

Le moyen le plus simple pour débuter est d'utiliser le CLI interactif :

```bash
# Lancer l'interface interactive
python slack-manager.py

# Ou via Makefile
make interactive
```

**Interface du menu principal :**

```
============================================================
  SLACK MANAGEMENT PLATFORM - Interactive CLI
============================================================

MAIN MENU
----------
1. User Management
2. Channel Management
3. Audit & Reports
4. Backup & Recovery
5. Workspace Statistics
6. Tools & Utilities
7. Exit

Enter your choice:
```

### 1.2 Commandes Makefile

Pour une utilisation avancée, utilisez directement les commandes Makefile :

```bash
# Afficher toutes les commandes disponibles
make help

# Tester la connexion Slack
make test

# Statistiques rapides
make stats
```

**Catégories de commandes :**

| Catégorie | Commande | Description |
|-----------|----------|-------------|
| **Général** | `make help` | Affiche l'aide complète |
| | `make install` | Installe les dépendances |
| | `make test` | Test la connexion API |
| **Utilisateurs** | `make list-users` | Liste tous les utilisateurs |
| | `make user-stats` | Statistiques utilisateurs |
| **Canaux** | `make list-channels` | Liste tous les canaux |
| **Audit** | `make audit-permissions` | Audit des permissions |
| **Backup** | `make backup` | Sauvegarde complète |

### 1.3 Exécution directe des scripts

```bash
# Format général
python scripts/<catégorie>/<script>.py [options]

# Exemple
python scripts/users/list_users.py --role admin
```

---

## 👥 2. Gestion des utilisateurs

### 2.1 Lister les utilisateurs

**Tous les utilisateurs :**

```bash
# Via Makefile
make list-users

# Via script direct
python scripts/users/list_users.py
```

**Filtrer par rôle :**

```bash
# Administrateurs uniquement
make list-admins
python scripts/users/list_users.py --role admin

# Invités uniquement
make list-guests
python scripts/users/list_users.py --role guest
```

**Sortie type :**

```
📊 WORKSPACE USERS
==================

👤 John Doe
   📧 john.doe@company.com
   🆔 U01234567
   👑 Admin | ✅ Active

👤 Jane Smith
   📧 jane.smith@company.com
   🆔 U89012345
   👤 Member | ✅ Active

Total: 127 users (5 admins, 12 guests, 110 members)
```

### 2.2 Statistiques des utilisateurs

```bash
# Via Makefile
make user-stats

# Via script
python scripts/users/user_stats.py
```

**Informations affichées :**

- 📊 Nombre total d'utilisateurs
- 👑 Répartition par rôle (admins, membres, invités)
- ✅ Utilisateurs actifs vs désactivés
- 📅 Tendances d'inscription
- 🌍 Répartition par fuseaux horaires

### 2.3 Exporter les utilisateurs

**Format CSV :**

```bash
# Export CSV simple
make export-users

# Export CSV avec options
python scripts/users/export_users.py --format csv --output users.csv
```

**Format JSON :**

```bash
# Export JSON
make export-users-json

# Export JSON avec filtres
python scripts/users/export_users.py --format json --role admin --output admins.json
```

**Contenu du fichier CSV généré :**

| user_id | email | real_name | role | status | created_date |
|---------|-------|-----------|------|--------|--------------|
| U01234 | john@company.com | John Doe | admin | active | 2024-01-15 |
| U56789 | jane@company.com | Jane Smith | member | active | 2024-02-20 |

### 2.4 Inviter des utilisateurs

**Préparer le fichier CSV :**

Créez un fichier `new_users.csv` :

```csv
email,first_name,last_name,role
alice@company.com,Alice,Johnson,member
bob@company.com,Bob,Williams,member
admin@company.com,Admin,User,admin
```

**Inviter depuis le CSV :**

```bash
# Avec validation (dry-run)
python scripts/users/invite_users.py --file new_users.csv --dry-run

# Invitation réelle
make invite-users FILE=new_users.csv

# Avec canal d'accueil personnalisé
python scripts/users/invite_users.py --file new_users.csv --channel welcome
```

**Options avancées :**

```bash
# Générer un template CSV
make template TYPE=users

# Valider le CSV avant import
make validate-csv FILE=new_users.csv

# Invitation avec resend pour emails échoués
python scripts/users/invite_users.py --file users.csv --resend-failed
```

### 2.5 Désactiver un utilisateur

```bash
# Désactiver un utilisateur spécifique
make deactivate-user EMAIL=user@company.com

# Avec confirmation interactive
python scripts/users/deactivate_user.py --email user@company.com --interactive

# Mode dry-run pour tester
python scripts/users/deactivate_user.py --email user@company.com --dry-run
```

**Processus de désactivation :**

1. ✅ Vérification de l'existence de l'utilisateur
2. 🔍 Affichage des informations utilisateur
3. ⚠️  Demande de confirmation
4. 🔒 Désactivation du compte
5. 📧 Notification envoyée (optionnel)

### 2.6 Rechercher des utilisateurs

```bash
# Recherche universelle
make search QUERY="john"

# Recherche avancée avec filtres
python scripts/tools/search.py --query "admin" --type user --limit 10
```

---

## 💬 3. Gestion des canaux

### 3.1 Lister les canaux

**Canaux publics :**

```bash
# Via Makefile
make list-channels

# Tous les canaux (publics, privés, archivés)
make list-channels-all

# Via script
python scripts/channels/list_channels.py --include-private --include-archived
```

**Sortie exemple :**

```
📢 WORKSPACE CHANNELS
====================

#general
  👥 Members: 127
  📝 Public | 🔓 Not Archived
  📅 Created: 2023-01-15

#random
  👥 Members: 98
  📝 Public | 🔓 Not Archived
  📅 Created: 2023-01-15

#old-project
  👥 Members: 5
  📝 Private | 📦 Archived
  📅 Last activity: 2023-06-20

Total: 45 channels (35 public, 10 private, 8 archived)
```

### 3.2 Créer des canaux

**Préparer le fichier CSV :**

Créez `new_channels.csv` :

```csv
name,topic,description,is_private
project-alpha,Project Alpha,Channel for Project Alpha team,false
hr-confidential,HR Matters,Private HR discussions,true
team-marketing,Marketing,Marketing team coordination,false
```

**Créer les canaux :**

```bash
# Avec dry-run (recommandé)
python scripts/channels/create_channels.py --file new_channels.csv --dry-run

# Création réelle
make create-channels FILE=new_channels.csv

# Avec ajout automatique de membres
python scripts/channels/create_channels.py --file channels.csv --add-creator
```

**Options de création :**

- `--is-private` : Créer un canal privé
- `--add-creator` : Ajouter automatiquement le créateur
- `--invite-users` : Inviter une liste d'utilisateurs

### 3.3 Archiver des canaux

**Archiver un canal unique :**

```bash
# Via Makefile
make archive-channel NAME=old-project

# Via script avec confirmation
python scripts/channels/archive_channel.py --name old-project --confirm

# Mode dry-run
python scripts/channels/archive_channel.py --name old-project --dry-run
```

**Détecter les canaux inactifs :**

```bash
# Canaux inactifs depuis 90 jours
make find-inactive

# Personnaliser le délai
make find-inactive DAYS=180

# Export des résultats
python scripts/channels/find_inactive.py --days 90 --export inactive_channels.csv
```

**Rapport d'inactivité :**

```
🔍 INACTIVE CHANNELS (90+ days)
================================

#old-project-2023
  👥 Members: 3
  📅 Last message: 2024-01-15 (245 days ago)
  💬 Total messages: 47

#temp-event
  👥 Members: 12
  📅 Last message: 2024-03-20 (181 days ago)
  💬 Total messages: 234

Recommendation: 12 channels eligible for archiving
```

### 3.4 Gérer les membres

```bash
# Lister les membres d'un canal
python scripts/channels/manage_members.py --channel general --action list

# Ajouter des membres
python scripts/channels/manage_members.py --channel project-alpha --action add --users user1@company.com,user2@company.com

# Retirer un membre
python scripts/channels/manage_members.py --channel old-team --action remove --users former@company.com

# Export des membres vers CSV
python scripts/channels/manage_members.py --channel general --action export --output general_members.csv
```

---

## 🔍 4. Audit et conformité

### 4.1 Audit des permissions

**Audit complet :**

```bash
# Audit standard
make audit-permissions

# Export vers CSV
make audit-permissions-csv

# Audit détaillé avec recommandations
python scripts/audit/permissions_audit.py --detailed --recommendations
```

**Résultat de l'audit :**

```
🔐 PERMISSIONS AUDIT
====================

👑 ADMINISTRATORS (5)
  ✅ john.doe@company.com - Owner
  ⚠️  temp.admin@company.com - Admin (created 2 days ago)

🔓 EXCESSIVE PERMISSIONS DETECTED
  ⚠️  3 users with admin rights created in last 30 days
  ⚠️  2 guest users with unusual channel access

📊 RECOMMENDATIONS
  1. Review recent admin promotions
  2. Audit guest user permissions
  3. Enable 2FA for all admins
```

### 4.2 Utilisateurs inactifs

```bash
# Détecter les utilisateurs inactifs (60 jours par défaut)
make inactive-users

# Personnaliser le délai
make inactive-users DAYS=30

# Export avec détails
python scripts/audit/inactive_users.py --days 90 --export inactive.csv --include-stats
```

**Rapport généré :**

| Email | Last Active | Days Inactive | Total Messages | Status |
|-------|-------------|---------------|----------------|--------|
| old.user@company.com | 2024-01-15 | 245 | 12 | Active |
| temp.worker@company.com | 2024-03-20 | 181 | 156 | Active |

### 4.3 Détection de doublons

```bash
# Trouver les utilisateurs en double
make find-duplicates

# Recherche approfondie
python scripts/audit/find_duplicates.py --check-emails --check-names --fuzzy
```

**Doublons détectés :**

```
👥 POTENTIAL DUPLICATES
=======================

⚠️  Duplicate emails detected:
   • john.doe@company.com (2 accounts)
     - U01234567 (Active)
     - U98765432 (Deactivated)

⚠️  Similar names detected:
   • "John Smith" / "J. Smith" (90% match)
   • "Marketing Team" / "Marketing-Team" (95% match)
```

### 4.4 Rapport d'activité

```bash
# Rapport sur 30 jours
make activity-report DAYS=30

# Rapport détaillé
python scripts/audit/activity_report.py --days 30 --detailed --format pdf
```

**Métriques du rapport :**

- 📊 Messages envoyés par jour
- 👥 Utilisateurs actifs uniques
- 💬 Canaux les plus actifs
- 📈 Tendances d'engagement
- 🕐 Heures de pointe d'activité

### 4.5 Export de l'historique des canaux

```bash
# Exporter un canal spécifique
make export-channel CHANNEL=general

# Export avec limite de messages
python scripts/audit/export_channel_history.py --channel general --limit 1000

# Export de tous les canaux publics
python scripts/audit/export_channel_history.py --all-public --output-dir exports/
```

---

## 💾 5. Sauvegardes

### 5.1 Sauvegarde standard

```bash
# Sauvegarde rapide (métadonnées uniquement)
make backup

# Sauvegarde dans un répertoire spécifique
python scripts/backup/create_backup.py --output-dir backups/
```

**Contenu de la sauvegarde :**

```
backups/
└── 2024-11-17_14-30-45/
    ├── users.json          # Tous les utilisateurs
    ├── channels.json       # Tous les canaux
    ├── workspaces.json     # Configuration workspace
    ├── permissions.json    # Matrice de permissions
    └── metadata.json       # Métadonnées de backup
```

### 5.2 Sauvegarde complète

```bash
# Backup avec historique des messages
make backup-full

# Backup personnalisé
python scripts/backup/create_backup.py \
  --output-dir backups/ \
  --include-messages \
  --message-limit 1000 \
  --include-files
```

**Options disponibles :**

| Option | Description | Impact |
|--------|-------------|--------|
| `--include-messages` | Inclure l'historique | +++ Temps |
| `--message-limit N` | Limiter à N messages/canal | Taille contrôlée |
| `--include-files` | Sauvegarder métadonnées fichiers | ++ Taille |
| `--compress` | Compresser en .zip | - Taille |

### 5.3 Comparaison de sauvegardes

```bash
# Comparer deux backups
make compare-backups B1=backups/2024-11-01 B2=backups/2024-11-17

# Format détaillé
python scripts/backup/compare_backups.py \
  backups/2024-11-01 \
  backups/2024-11-17 \
  --format detailed
```

**Rapport de comparaison :**

```
📊 BACKUP COMPARISON
====================

📅 Period: 2024-11-01 → 2024-11-17

👥 USERS
  ✅ Added: 12 users
  ❌ Removed: 3 users
  🔄 Modified: 5 users

💬 CHANNELS
  ✅ Created: 8 channels
  📦 Archived: 4 channels
  🔄 Modified: 15 channels

⚠️  CRITICAL CHANGES
  • 2 admin users promoted
  • 1 channel made private
```

### 5.4 Automatisation des sauvegardes

**Créer une tâche cron :**

```bash
# Editer crontab
crontab -e

# Sauvegarde quotidienne à 2h du matin
0 2 * * * cd /home/user/slack-toolbox && make backup >> logs/backup.log 2>&1

# Sauvegarde complète hebdomadaire (dimanche 3h)
0 3 * * 0 cd /home/user/slack-toolbox && make backup-full >> logs/backup-full.log 2>&1
```

**Script de sauvegarde automatique fourni :**

```bash
# Utiliser le script cron fourni
cp cron/backup.sh /etc/cron.daily/slack-backup
chmod +x /etc/cron.daily/slack-backup
```

---

## 📊 6. Monitoring et alertes

### 6.1 Statistiques du workspace

```bash
# Vue d'ensemble rapide
make stats

# Statistiques détaillées
python scripts/reports/workspace_stats.py --detailed

# Export JSON
python scripts/reports/workspace_stats.py --format json --output stats.json
```

**Dashboard de statistiques :**

```
📊 WORKSPACE STATISTICS
=======================

👥 USERS
  Total: 127
  Active: 119 (93.7%)
  Admins: 5 (3.9%)
  Guests: 12 (9.4%)

💬 CHANNELS
  Total: 45
  Public: 35 (77.8%)
  Private: 10 (22.2%)
  Archived: 8 (17.8%)

📨 ACTIVITY (30 days)
  Messages: 12,547
  Files shared: 324
  Active users: 98 (77.2%)

💾 STORAGE
  Used: 23.5 GB / 50 GB (47%)
  Files: 2,341
```

### 6.2 Dashboard HTML

```bash
# Générer dashboard interactif
make dashboard

# Ouvrir dans le navigateur
xdg-open dashboard.html  # Linux
open dashboard.html      # macOS
```

**Fonctionnalités du dashboard :**

- 📊 Graphiques interactifs
- 📈 Tendances temporelles
- 🎯 KPIs en temps réel
- 📋 Tableaux détaillés
- 🔄 Auto-refresh (optionnel)

### 6.3 Alertes intelligentes

```bash
# Vérification simple
make smart-alerts

# Avec notifications Slack
make smart-alerts-notify

# Avec comparaison historique
make smart-alerts-compare
```

**Alertes détectées automatiquement :**

```
🔔 SMART ALERTS
===============

⚠️  HIGH PRIORITY
  • Storage usage: 94% (threshold: 90%)
  • 15 inactive users (90+ days)
  • Unusual admin activity detected

⚡ MEDIUM PRIORITY
  • 8 channels with no activity (30 days)
  • Guest user count increased 40% this month

✅ LOW PRIORITY
  • 3 channels ready for archival
  • Backup older than 7 days
```

### 6.4 Notifications personnalisées

```bash
# Envoyer une notification simple
make notify MSG="Backup terminé avec succès"

# Notification avec type spécifique
make notify MSG="Erreur critique détectée" TYPE=error

# Notification vers un canal spécifique
python scripts/monitoring/send_notification.py \
  --message "Rapport hebdomadaire prêt" \
  --channel "#admin" \
  --type info
```

**Types de notifications :**

- ✅ `success` : Opération réussie
- ℹ️  `info` : Information générale
- ⚠️  `warning` : Avertissement
- ❌ `error` : Erreur critique

### 6.5 Rapports PDF

```bash
# Générer rapport utilisateurs en PDF
make export-pdf TYPE=users OUTPUT=users_report.pdf

# Rapport de permissions
python scripts/reports/export_pdf.py --type permissions --output audit.pdf

# Rapport complet workspace
python scripts/reports/export_pdf.py --type workspace --detailed --output workspace_full.pdf
```

---

## 💡 7. Exemples pratiques

### 7.1 Onboarding de nouveaux employés

**Scénario :** 10 nouveaux employés rejoignent l'entreprise

```bash
# 1. Créer le fichier CSV
cat > new_hires.csv << EOF
email,first_name,last_name,role
alice.martin@company.com,Alice,Martin,member
bob.dubois@company.com,Bob,Dubois,member
charlie.bernard@company.com,Charlie,Bernard,member
EOF

# 2. Valider le CSV
make validate-csv FILE=new_hires.csv

# 3. Test avec dry-run
python scripts/users/invite_users.py --file new_hires.csv --dry-run

# 4. Inviter réellement
make invite-users FILE=new_hires.csv

# 5. Ajouter aux canaux d'équipe
python scripts/channels/manage_members.py \
  --channel team-general \
  --action add \
  --users alice.martin@company.com,bob.dubois@company.com

# 6. Envoyer notification
make notify MSG="10 nouveaux employés ajoutés au workspace" CHANNEL="#admin"
```

### 7.2 Audit mensuel de sécurité

**Scénario :** Audit de sécurité régulier le 1er de chaque mois

```bash
#!/bin/bash
# Script: monthly_security_audit.sh

DATE=$(date +%Y-%m-%d)
REPORT_DIR="audits/$DATE"
mkdir -p "$REPORT_DIR"

# 1. Audit des permissions
echo "🔐 Audit des permissions..."
python scripts/audit/permissions_audit.py --export "$REPORT_DIR/permissions.csv"

# 2. Utilisateurs inactifs
echo "👥 Détection utilisateurs inactifs..."
python scripts/audit/inactive_users.py --days 60 --export "$REPORT_DIR/inactive.csv"

# 3. Détection de doublons
echo "🔍 Recherche de doublons..."
python scripts/audit/find_duplicates.py --export "$REPORT_DIR/duplicates.csv"

# 4. Rapport d'activité
echo "📊 Génération rapport d'activité..."
python scripts/audit/activity_report.py --days 30 --format pdf --output "$REPORT_DIR/activity.pdf"

# 5. Générer dashboard
echo "📈 Création dashboard..."
python scripts/reports/generate_dashboard.py --output "$REPORT_DIR/dashboard.html"

# 6. Notification finale
make notify MSG="✅ Audit de sécurité mensuel terminé - Voir audits/$DATE" CHANNEL="#security"

echo "✅ Audit terminé ! Rapports dans: $REPORT_DIR"
```

### 7.3 Nettoyage trimestriel

**Scénario :** Nettoyer les canaux et utilisateurs inactifs chaque trimestre

```bash
#!/bin/bash
# Script: quarterly_cleanup.sh

echo "🧹 Nettoyage trimestriel du workspace"

# 1. Identifier les canaux inactifs (90 jours)
echo "📢 Recherche canaux inactifs..."
python scripts/channels/find_inactive.py --days 90 --export cleanup/inactive_channels.csv

# 2. Identifier les utilisateurs inactifs (180 jours)
echo "👥 Recherche utilisateurs inactifs..."
python scripts/audit/inactive_users.py --days 180 --export cleanup/inactive_users.csv

# 3. Backup avant nettoyage
echo "💾 Sauvegarde de sécurité..."
make backup-full

# 4. Revue manuelle (afficher les résultats)
echo ""
echo "📋 RÉSULTATS - Action manuelle requise:"
echo "  • Canaux inactifs: cleanup/inactive_channels.csv"
echo "  • Utilisateurs inactifs: cleanup/inactive_users.csv"
echo ""
echo "Commandes suggérées après revue:"
echo "  - Archiver canal: make archive-channel NAME=<channel-name>"
echo "  - Désactiver user: make deactivate-user EMAIL=<user@email>"
```

### 7.4 Migration d'équipe

**Scénario :** Créer une nouvelle équipe projet avec canaux et membres

```bash
# 1. Créer les canaux pour le projet
cat > project_phoenix_channels.csv << EOF
name,topic,description,is_private
phoenix-general,Phoenix Project,General discussions,false
phoenix-dev,Development,Development team only,true
phoenix-design,Design,Design discussions,false
phoenix-management,Project Management,PM and leads only,true
EOF

make create-channels FILE=project_phoenix_channels.csv

# 2. Inviter les membres de l'équipe
cat > project_phoenix_team.csv << EOF
email,first_name,last_name,role
lead@company.com,Project,Lead,member
dev1@company.com,Developer,One,member
dev2@company.com,Developer,Two,member
designer@company.com,Lead,Designer,member
EOF

make invite-users FILE=project_phoenix_team.csv

# 3. Ajouter tous aux canaux appropriés
python scripts/channels/manage_members.py \
  --channel phoenix-general \
  --action add \
  --users lead@company.com,dev1@company.com,dev2@company.com,designer@company.com

python scripts/channels/manage_members.py \
  --channel phoenix-dev \
  --action add \
  --users lead@company.com,dev1@company.com,dev2@company.com

# 4. Notification de création
make notify MSG="🚀 Projet Phoenix créé - Canaux et équipe configurés" CHANNEL="#announcements"
```

### 7.5 Rapport hebdomadaire automatisé

**Configuration cron pour rapport hebdomadaire (chaque lundi 9h) :**

```bash
# Ajouter à crontab
0 9 * * 1 /home/user/slack-toolbox/scripts/weekly_report.sh
```

**Script weekly_report.sh :**

```bash
#!/bin/bash
cd /home/user/slack-toolbox

WEEK=$(date +%Y-W%U)
REPORT_DIR="reports/weekly/$WEEK"
mkdir -p "$REPORT_DIR"

# Statistiques workspace
python scripts/reports/workspace_stats.py \
  --format json \
  --output "$REPORT_DIR/stats.json"

# Rapport d'activité 7 jours
python scripts/audit/activity_report.py \
  --days 7 \
  --format pdf \
  --output "$REPORT_DIR/activity.pdf"

# Alertes intelligentes
python scripts/monitoring/smart_alerts.py \
  --export "$REPORT_DIR/alerts.json"

# Dashboard HTML
python scripts/reports/generate_dashboard.py \
  --output "$REPORT_DIR/dashboard.html"

# Envoyer notification avec lien
make notify \
  MSG="📊 Rapport hebdomadaire disponible: reports/weekly/$WEEK/dashboard.html" \
  CHANNEL="#management"
```

---

## 🎯 Conseils et bonnes pratiques

### ✅ À faire

- 🧪 **Toujours tester** avec `--dry-run` avant les opérations importantes
- 💾 **Sauvegarder régulièrement** votre workspace (quotidien recommandé)
- 📊 **Monitorer** les alertes intelligentes hebdomadairement
- 🔍 **Auditer** les permissions mensuellement
- 📝 **Valider** les CSV avant import massif

### ❌ À éviter

- ⚠️  Ne jamais désactiver des utilisateurs sans backup récent
- ⚠️  Ne pas archiver des canaux sans vérifier l'activité récente
- ⚠️  Éviter les invitations massives sans validation préalable
- ⚠️  Ne pas ignorer les alertes de sécurité
- ⚠️  Ne jamais partager vos tokens API

---

## 🆘 Besoin d'aide ?

- 📚 **Documentation complète** : [Wiki](../wiki/)
- 🐛 **Problèmes** : [GitHub Issues](https://github.com/GitCroque/slack-toolbox/issues)
- 💬 **Questions** : [FAQ](./FAQ.md)
- 🔐 **Sécurité** : [Guide Sécurité](./SECURITE.md)

---

**🌟 Dernière mise à jour : Novembre 2024 | Version : 2.0**
