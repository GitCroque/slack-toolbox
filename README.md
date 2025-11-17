# 🚀 Slack Toolbox

> **Suite professionnelle pour gérer votre espace de travail Slack**

Gérez facilement vos utilisateurs, canaux, sauvegardes et audits avec des outils CLI puissants.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-213%20passent-success)](./tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ⚡ Démarrage Rapide

```bash
# Installation
git clone https://github.com/GitCroque/slack-toolbox.git
cd slack-toolbox
python3 setup_wizard.py

# Utilisation
python slack-manager.py
```

C'est tout ! L'assistant configure automatiquement votre environnement.

---

## ✨ Fonctionnalités

| Catégorie | Fonctionnalités |
|-----------|----------------|
| **👥 Utilisateurs** | Lister, inviter, exporter, désactiver, statistiques |
| **💬 Canaux** | Créer, archiver, gérer membres, détecter inactifs |
| **🔍 Audit** | Permissions, activité, doublons, conformité |
| **💾 Sauvegarde** | Backup complet, comparaison, export historique |
| **📊 Rapports** | Stats, dashboards, PDF, alertes intelligentes |

---

## 📚 Documentation

📖 **Toute la documentation est disponible sur le [Wiki](https://github.com/GitCroque/slack-toolbox/wiki)**

### Documentation principale

- **[Installation](https://github.com/GitCroque/slack-toolbox/wiki/INSTALLATION)** - Guide d'installation complet
- **[Configuration](https://github.com/GitCroque/slack-toolbox/wiki/CONFIGURATION)** - Configuration détaillée
- **[Utilisation](https://github.com/GitCroque/slack-toolbox/wiki/UTILISATION)** - Guide utilisateur
- **[Quick Start](https://github.com/GitCroque/slack-toolbox/wiki/QUICKSTART)** - Démarrage rapide
- **[Exemples](https://github.com/GitCroque/slack-toolbox/wiki/EXAMPLES)** - 30+ exemples pratiques
- **[FAQ](https://github.com/GitCroque/slack-toolbox/wiki/FAQ)** - Questions fréquentes

### Pour les développeurs

- **[Architecture](https://github.com/GitCroque/slack-toolbox/wiki/ARCHITECTURE)** - Architecture technique
- **[Développement](https://github.com/GitCroque/slack-toolbox/wiki/DEVELOPPEMENT)** - Guide développeur
- **[Contributing](https://github.com/GitCroque/slack-toolbox/wiki/CONTRIBUTING)** - Comment contribuer
- **[API Slack Guide](https://github.com/GitCroque/slack-toolbox/wiki/SLACK_API_GUIDE)** - Guide complet API

### Sécurité & Automatisation

- **[Sécurité](https://github.com/GitCroque/slack-toolbox/wiki/SECURITE)** - Bonnes pratiques sécurité
- **[Automatisation](https://github.com/GitCroque/slack-toolbox/wiki/CRON_AUTOMATION)** - Scripts cron

> 💡 **Les fichiers dans `./wiki/` sont les sources.** La documentation complète est publiée sur le [Wiki GitHub](https://github.com/GitCroque/slack-toolbox/wiki).

---

## 🎯 Exemples

```bash
# Lister les utilisateurs
make list-users

# Inviter depuis CSV
make invite-users

# Audit de permissions
make audit-permissions

# Sauvegarde complète
make backup

# Alertes intelligentes
make smart-alerts
```

Plus de 60 commandes disponibles via `make help`

---

## 🔐 Sécurité

- ✅ Validation complète des entrées
- ✅ Mode dry-run pour tester sans risque
- ✅ Tokens jamais loggés
- ✅ Scan sécurité automatique (Bandit, Safety)
- ✅ Pre-commit hooks

Voir [wiki/SECURITE.md](./wiki/SECURITE.md) pour plus de détails.

---

## 🧪 Tests

```bash
make test              # Lancer tous les tests
make test-coverage     # Tests avec couverture
```

**213 tests** | **98.6% de succès** | **~45% de couverture**

---

## 🤝 Contribution

Les contributions sont bienvenues ! Consultez [wiki/DEVELOPPEMENT.md](./wiki/DEVELOPPEMENT.md)

```bash
git checkout -b feature/ma-fonctionnalite
make test && make lint
git commit -m "Add: Ma fonctionnalité"
```

---

## 📄 Licence

MIT - Voir [LICENSE](LICENSE)

---

## 🌟 Support

- **Documentation** : [Wiki complet](./wiki/)
- **Issues** : [GitHub Issues](https://github.com/GitCroque/slack-toolbox/issues)
- **Email** : gitcroque@example.com

---

**⭐ Si ce projet vous aide, donnez-lui une étoile !**
