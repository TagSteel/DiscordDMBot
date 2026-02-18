# DickBot - Bot Discord

Bot Discord avec une commande slash qui envoie une notification privée à un utilisateur pour l'informer qu'il a été mentionné.

## 📋 Fonctionnalités

- **Commande `/setcible`** (Admin seulement) : Définit l'utilisateur qui recevra les notifications
- **Commande `/gorgeprofonde`** : Envoie un message privé à l'utilisateur cible en lui indiquant :
  - Qui l'a pingé
  - Sur quel serveur
  - Dans quel salon
  - Message visible par tous dans le salon

## 🚀 Installation

### 1. Prérequis

- Python 3.8+ installé
- Un compte Discord Developer

### 2. Créer une application Discord

1. Allez sur [Discord Developer Portal](https://discord.com/developers/applications)
2. Cliquez sur "New Application"
3. Donnez un nom à votre bot et créez-le
4. Allez dans l'onglet "Bot"
5. Cliquez sur "Reset Token" et copiez le token (gardez-le secret !)
6. Activez les "Privileged Gateway Intents" suivants :
   - SERVER MEMBERS INTENT
   - MESSAGE CONTENT INTENT

### 3. Inviter le bot sur votre serveur

1. Allez dans l'onglet "OAuth2" > "URL Generator"
2. Sélectionnez les scopes :
   - `bot`
   - `applications.commands`
3. Sélectionnez les permissions :
   - Send Messages
   - Use Slash Commands
   - Read Messages/View Channels
4. Copiez l'URL générée et ouvrez-la dans votre navigateur
5. Sélectionnez votre serveur et autorisez le bot

### 4. Configuration du projet

```bash
# Installer les dépendances Python
pip install -r requirements.txt

# Créer le fichier .env
cp .env.example .env
```

Éditez le fichier `.env` et ajoutez votre token Discord :
```
DISCORD_TOKEN=votre_token_discord_ici
```

### 5. Lancer le bot

```bash
# Lancer le bot
python bot.py

# Alternative avec python3
python3 bot.py
```

## 📖 Utilisation

Une fois le bot en ligne sur votre serveur :

### Configuration initiale (Admin)

1. Un administrateur doit d'abord définir la cible avec `/setcible @utilisateur`
2. Cette cible sera la seule personne à recevoir les notifications

### Utilisation normale

1. N'importe qui peut taper `/gorgeprofonde` dans un salon
2. L'utilisateur cible recevra un message privé avec :
   - Le nom de la personne qui l'a pingé
   - Le nom du serveur
   - Le nom du salon
3. Un message de confirmation visible par tous apparaîtra dans le salon

## ⚠️ Notes importantes

- Un administrateur doit d'abord configurer l'utilisateur cible avec `/setcible`
- Une seule personne peut être définie comme cible par serveur
- L'utilisateur ciblé doit autoriser les messages privés pour recevoir la notification
- La commande est visible par tous dans le salon (pas de message éphémère)
- Le bot a besoin d'être en ligne pour fonctionner
- La configuration est sauvegardée dans `config.json`

## 🛠️ Technologies utilisées

- [discord.py](https://discordpy.readthedocs.io/) v2.3
- Python 3.8+
- python-dotenv

## 📝 Licence

MIT
