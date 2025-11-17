# 📦 Guide d'Installation

Guide complet pour installer Slack Toolbox sur votre système.

---

## 📋 Prérequis

### Système
- **Python** : 3.8 ou supérieur
- **pip** : Gestionnaire de paquets Python
- **git** : Pour cloner le dépôt
- **OS supportés** : Linux, macOS, Windows (WSL recommandé)

### Espace Slack
- Token d'application Slack (voir [Configuration](./CONFIGURATION.md))
- Permissions appropriées sur l'espace de travail

---

## ⚡ Méthode 1 : Installation Automatique (Recommandée)

L'assistant de configuration fait tout pour vous !

```bash
# 1. Cloner le dépôt
git clone https://github.com/GitCroque/slack-toolbox.git
cd slack-toolbox

# 2. Lancer l'assistant
python3 setup_wizard.py
```

L'assistant va :
- ✅ Vérifier les prérequis système
- ✅ Installer toutes les dépendances Python
- ✅ Créer la configuration
- ✅ Tester la connexion Slack
- ✅ Configurer les hooks git (optionnel)
- ✅ Installer les pre-commit hooks (optionnel)

C'est terminé ! Passez directement à [Utilisation](./UTILISATION.md).

---

## 🔧 Méthode 2 : Installation Manuelle

### Étape 1 : Cloner le Dépôt

```bash
git clone https://github.com/GitCroque/slack-toolbox.git
cd slack-toolbox
```

### Étape 2 : Environnement Virtuel (Recommandé)

```bash
# Créer l'environnement virtuel
python3 -m venv venv

# Activer (Linux/macOS)
source venv/bin/activate

# Activer (Windows)
venv\Scripts\activate
```

### Étape 3 : Installer les Dépendances

```bash
# Installation de base
pip install -r requirements.txt

# OU installation complète (avec PDF, dev, test)
pip install -e ".[all]"

# OU installation sélective
pip install -e ".[pdf]"      # Support PDF
pip install -e ".[dev]"      # Outils développement
pip install -e ".[test]"     # Outils de test
```

### Étape 4 : Configuration

```bash
# Copier la configuration exemple
cp config/config.example.json config/config.json

# Éditer avec votre token
nano config/config.json
```

Voir [Configuration](./CONFIGURATION.md) pour obtenir votre token.

### Étape 5 : Test de Connexion

```bash
python scripts/tools/test_connection.py
```

Vous devriez voir :
```
✅ Connecté à l'espace de travail Slack: VotreEntreprise
   Utilisateur bot: @votre-bot
```

---

## 📦 Méthode 3 : Installation via pip (Package)

Installation directe depuis PyPI :

```bash
# Installation de base
pip install slack-management-platform

# Installation complète
pip install slack-management-platform[all]
```

Puis configurez votre token :

```bash
# Créer le dossier config
mkdir -p ~/.slack-toolbox

# Créer la configuration
cat > ~/.slack-toolbox/config.json << EOF
{
  "slack_token": "xoxb-votre-token-ici",
  "max_retries": 3,
  "rate_limit_delay": 1
}
EOF
```

---

## 🐳 Méthode 4 : Installation Docker (À venir)

```bash
# Pull l'image
docker pull gitcroque/slack-toolbox:latest

# Lancer avec votre config
docker run -v $(pwd)/config:/app/config gitcroque/slack-toolbox
```

---

## 🛠️ Installation Développement

Pour contribuer au projet :

```bash
# 1. Fork et cloner
git clone https://github.com/VOUS/slack-toolbox.git
cd slack-toolbox

# 2. Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# 3. Installer avec dépendances dev
pip install -e ".[dev,test]"

# 4. Installer pre-commit hooks
pre-commit install

# 5. Vérifier l'installation
make test
make lint
```

Voir [Développement](./DEVELOPPEMENT.md) pour plus de détails.

---

## 🎯 Vérification de l'Installation

### Test Rapide

```bash
# Tester la connexion
make test-connection

# Lancer le gestionnaire
python slack-manager.py

# Afficher l'aide
make help
```

### Exécuter les Tests

```bash
# Tous les tests
make test

# Tests avec couverture
make test-coverage

# Tests spécifiques
pytest tests/test_validators.py -v
```

### Vérifier les Commandes

```bash
# Liste de toutes les commandes Makefile
make help

# Devrait afficher 60+ commandes organisées par catégorie
```

---

## 🐛 Dépannage

### Python 3.8+ introuvable

**macOS** :
```bash
brew install python@3.11
```

**Ubuntu/Debian** :
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**Windows** :
- Télécharger depuis https://www.python.org/downloads/

### Erreur : "pip: command not found"

```bash
# macOS
brew install pip

# Ubuntu/Debian
sudo apt install python3-pip

# Vérifier
pip --version
```

### Erreur : "ModuleNotFoundError: No module named 'slack_sdk'"

```bash
# Réinstaller les dépendances
pip install -r requirements.txt

# Vérifier
python -c "import slack_sdk; print('OK')"
```

### Erreur : "Permission denied"

```bash
# Option 1 : Utiliser un environnement virtuel (recommandé)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Option 2 : Installation utilisateur
pip install --user -r requirements.txt
```

### Problème avec reportlab (PDF)

Le support PDF est optionnel. Si vous n'en avez pas besoin :

```bash
# Installation sans PDF
pip install slack-sdk requests

# Installer PDF plus tard si nécessaire
pip install reportlab
```

### Tests échouent

```bash
# Vérifier que toutes les dépendances sont installées
pip install -e ".[test]"

# Réexécuter
pytest -v
```

---

## 🔄 Mise à Jour

### Depuis Git

```bash
# Se placer dans le répertoire
cd slack-toolbox

# Pull les derniers changements
git pull origin main

# Mettre à jour les dépendances
pip install -r requirements.txt --upgrade

# Réexécuter les tests
make test
```

### Depuis pip

```bash
pip install --upgrade slack-management-platform
```

---

## 🗑️ Désinstallation

### Installation manuelle

```bash
# Supprimer le dossier
rm -rf slack-toolbox

# Désactiver l'environnement virtuel
deactivate
```

### Installation pip

```bash
pip uninstall slack-management-platform
```

---

## 📚 Prochaines Étapes

Maintenant que l'installation est terminée :

1. **[Configuration](./CONFIGURATION.md)** - Configurer votre token Slack
2. **[Utilisation](./UTILISATION.md)** - Apprendre à utiliser les outils
3. **[FAQ](./FAQ.md)** - Questions fréquentes

---

## 💡 Conseils

- Utilisez **toujours un environnement virtuel** pour isoler les dépendances
- Activez les **pre-commit hooks** pour maintenir la qualité du code
- Testez avec **--dry-run** avant toute modification importante
- Gardez votre **token sécurisé** et ne le commitez jamais

---

**Besoin d'aide ?** Consultez la [FAQ](./FAQ.md) ou ouvrez une [issue](https://github.com/GitCroque/slack-toolbox/issues).
