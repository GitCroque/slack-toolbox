# Exemples d'utilisation

Ce document présente des exemples concrets d'utilisation des scripts Slack.

## Configuration initiale

Avant d'utiliser les scripts, testez votre connexion :

```bash
python3 scripts/utils/test_connection.py
```

## Gestion des utilisateurs

### Lister tous les utilisateurs actifs

```bash
python3 scripts/users/list_users.py
```

### Lister uniquement les administrateurs

```bash
python3 scripts/users/list_users.py --role admin
```

### Exporter tous les utilisateurs en CSV

```bash
python3 scripts/users/export_users.py --format csv --output users.csv
```

### Inviter des utilisateurs depuis un fichier CSV

```bash
python3 scripts/users/invite_users.py --file examples/users.csv
```

### Inviter un utilisateur unique

```bash
python3 scripts/users/invite_users.py \
  --email nouvelutilisateur@example.com \
  --first-name Jean \
  --last-name Dupont \
  --channels general,random
```

### Désactiver un utilisateur

```bash
python3 scripts/users/deactivate_user.py --email utilisateur@example.com
```

### Afficher les statistiques utilisateurs

```bash
python3 scripts/users/user_stats.py
```

## Gestion des canaux

### Lister tous les canaux (publics et privés)

```bash
python3 scripts/channels/list_channels.py --include-private
```

### Lister avec le nombre de membres

```bash
python3 scripts/channels/list_channels.py --with-members
```

### Créer des canaux depuis un CSV

```bash
python3 scripts/channels/create_channels.py --file examples/channels.csv
```

### Créer un canal unique

```bash
python3 scripts/channels/create_channels.py \
  --name projet-beta \
  --description "Discussions sur le projet Beta"
```

### Archiver un canal

```bash
python3 scripts/channels/archive_channel.py --name ancien-projet
```

### Désarchiver un canal

```bash
python3 scripts/channels/archive_channel.py --name projet-actif --unarchive
```

### Ajouter des utilisateurs à un canal

```bash
python3 scripts/channels/manage_members.py \
  --channel general \
  --add user1@example.com,user2@example.com
```

### Ajouter tous les admins à un canal

```bash
python3 scripts/channels/manage_members.py \
  --channel leadership \
  --add-admins
```

### Retirer un utilisateur d'un canal

```bash
python3 scripts/channels/manage_members.py \
  --channel random \
  --remove user@example.com
```

### Trouver les canaux inactifs (90+ jours)

```bash
python3 scripts/channels/find_inactive.py --days 90 --export inactive_channels.csv
```

## Audit et rapports

### Exporter l'historique d'un canal

```bash
python3 scripts/audit/export_channel_history.py \
  --channel general \
  --limit 1000 \
  --output general_history.json
```

### Exporter l'historique avec filtre de dates

```bash
python3 scripts/audit/export_channel_history.py \
  --channel general \
  --after 2024-01-01 \
  --before 2024-12-31
```

### Trouver les utilisateurs inactifs

```bash
python3 scripts/audit/inactive_users.py --days 60 --export inactive_users.csv
```

### Audit des permissions

```bash
python3 scripts/audit/permissions_audit.py --export permissions.csv
```

### Rapport sur les fichiers partagés

```bash
python3 scripts/audit/file_report.py --limit 200 --export files_report.csv
```

### Fichiers d'un utilisateur spécifique

```bash
python3 scripts/audit/file_report.py --user john@example.com --limit 50
```

### Fichiers d'un canal spécifique

```bash
python3 scripts/audit/file_report.py --channel general --limit 100
```

## Utilitaires workspace

### Afficher les statistiques du workspace

```bash
python3 scripts/utils/workspace_stats.py
```

### Backup complet (métadonnées uniquement)

```bash
python3 scripts/utils/full_backup.py --output-dir backups
```

### Backup avec historique des messages

```bash
python3 scripts/utils/full_backup.py \
  --output-dir backups \
  --include-messages \
  --message-limit 500
```

## Scénarios d'utilisation courants

### Onboarding d'une nouvelle équipe

1. Préparez un fichier CSV avec les nouveaux utilisateurs
2. Invitez-les en masse :
   ```bash
   python3 scripts/users/invite_users.py --file nouveaux_employes.csv
   ```

### Nettoyage régulier

1. Trouvez les canaux inactifs :
   ```bash
   python3 scripts/channels/find_inactive.py --days 90 --export to_archive.csv
   ```
2. Vérifiez le fichier généré
3. Archivez si nécessaire

### Audit de sécurité mensuel

```bash
# Audit des permissions
python3 scripts/audit/permissions_audit.py --export audit_$(date +%Y%m).csv

# Utilisateurs inactifs
python3 scripts/audit/inactive_users.py --days 30 --export inactive_$(date +%Y%m).csv

# Statistiques générales
python3 scripts/utils/workspace_stats.py > stats_$(date +%Y%m).txt
```

### Migration vers de nouveaux canaux

```bash
# 1. Créer les nouveaux canaux
python3 scripts/channels/create_channels.py --file new_channels.csv

# 2. Ajouter les admins
python3 scripts/channels/manage_members.py --channel nouveau-canal --add-admins

# 3. Archiver l'ancien canal
python3 scripts/channels/archive_channel.py --name ancien-canal
```

## Tests avant production

Utilisez l'option `--dry-run` pour tester sans appliquer les changements :

```bash
# Test d'invitation
python3 scripts/users/invite_users.py --file users.csv --dry-run

# Test de création de canaux
python3 scripts/channels/create_channels.py --file channels.csv --dry-run
```

## Automatisation avec cron

Exemple de tâches cron pour macOS (éditer avec `crontab -e`) :

```cron
# Backup quotidien à 2h du matin
0 2 * * * cd /path/to/slack-script && python3 scripts/utils/full_backup.py

# Rapport hebdomadaire des utilisateurs inactifs (lundi à 9h)
0 9 * * 1 cd /path/to/slack-script && python3 scripts/audit/inactive_users.py --days 30 --export /path/to/reports/inactive_$(date +\%Y\%m\%d).csv

# Statistiques mensuelles (1er du mois à 8h)
0 8 1 * * cd /path/to/slack-script && python3 scripts/utils/workspace_stats.py > /path/to/reports/stats_$(date +\%Y\%m).txt
```

## Conseils de sécurité

1. **Toujours tester d'abord** : Utilisez `--dry-run` ou testez sur un workspace de test
2. **Faire des backups** : Avant toute opération de masse, faites un backup complet
3. **Vérifier les permissions** : Assurez-vous que votre token Slack a les bonnes permissions
4. **Ne pas commiter le config.json** : Gardez vos tokens secrets
5. **Rotation des tokens** : Changez régulièrement votre token Slack

## Support

Pour toute question ou problème, consultez le README.md ou ouvrez une issue sur GitHub.
