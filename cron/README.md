# Cron Job Examples

Scripts d'automatisation pour tâches récurrentes.

## Installation

### 1. Rendre les scripts exécutables

```bash
chmod +x cron/*.sh
```

### 2. Éditer les scripts

Modifiez les chemins et paramètres selon vos besoins dans chaque script.

### 3. Ajouter à crontab

```bash
crontab -e
```

## Scripts disponibles

### daily_backup.sh - Backup quotidien

Sauvegarde complète du workspace chaque jour à 2h du matin.

```cron
# Tous les jours à 2h du matin
0 2 * * * /path/to/slack-script/cron/daily_backup.sh
```

Fonctionnalités :
- Backup complet des métadonnées
- Nettoyage automatique (garde 30 derniers jours)
- Logs dans logs/

### weekly_inactive_report.sh - Rapport hebdomadaire

Génère un rapport des utilisateurs inactifs chaque lundi à 9h.

```cron
# Tous les lundis à 9h
0 9 * * 1 /path/to/slack-script/cron/weekly_inactive_report.sh
```

Fonctionnalités :
- Détecte les utilisateurs inactifs (30+ jours)
- Export CSV dans exports/
- Logs dans logs/

### monthly_audit.sh - Audit mensuel

Audit de sécurité complet le 1er de chaque mois à 8h.

```cron
# 1er de chaque mois à 8h
0 8 1 * * /path/to/slack-script/cron/monthly_audit.sh
```

Fonctionnalités :
- Audit des permissions
- Détection utilisateurs inactifs (60+ jours)
- Détection de doublons
- Rapport d'activité
- Dashboard HTML
- Logs dans logs/

## Exemples additionnels

### Backup hebdomadaire avec messages

```cron
# Tous les dimanches à 3h du matin
0 3 * * 0 /path/to/slack-script/scripts/utils/full_backup.py --include-messages --message-limit 500
```

### Statistiques quotidiennes

```cron
# Tous les jours à 8h
0 8 * * * /path/to/slack-script/scripts/utils/workspace_stats.py > /path/to/stats_$(date +\%Y\%m\%d).txt
```

### Nettoyage de canaux inactifs (mensuel)

```cron
# 15 de chaque mois à 10h
0 10 15 * * /path/to/slack-script/scripts/channels/find_inactive.py --days 90 --export /path/to/inactive_channels.csv
```

## Notifications

Pour recevoir des notifications par email :

### macOS (avec postfix configuré)

```bash
# À la fin du script
echo "Backup completed" | mail -s "Slack Backup" admin@example.com
```

### Slack Webhook

Créer un webhook entrant et ajouter :

```bash
WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Backup quotidien terminé ✅"}' \
  "$WEBHOOK_URL"
```

## Monitoring

### Vérifier les logs

```bash
# Derniers logs de backup
tail -f logs/daily_backup_*.log

# Logs d'aujourd'hui
tail -f logs/*$(date +%Y%m%d).log
```

### Lister les cron jobs actifs

```bash
crontab -l
```

## Bonnes pratiques

1. **Tester d'abord** : Exécutez manuellement avant d'ajouter à cron
   ```bash
   ./cron/daily_backup.sh
   ```

2. **Chemins absolus** : Utilisez toujours des chemins absolus dans les scripts

3. **Logs** : Conservez les logs pour débugger

4. **Notifications** : Configurez des alertes pour les échecs

5. **Rotation** : Nettoyez régulièrement les vieux backups et logs

6. **Permissions** : Assurez-vous que les scripts sont exécutables

## Troubleshooting

### Le cron ne s'exécute pas

1. Vérifier que le chemin est absolu
2. Vérifier les permissions (chmod +x)
3. Vérifier les logs système : `grep CRON /var/log/system.log` (macOS)

### Erreur "command not found"

Ajouter les chemins complets dans le script :

```bash
PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
export PATH
```

### Python non trouvé

Utiliser le chemin complet de Python :

```bash
/usr/bin/python3 scripts/...
# ou
/usr/local/bin/python3 scripts/...
```

## Support

Pour toute question, consultez :
- README.md principal
- SLACK_API_GUIDE.md
- FAQ.md
