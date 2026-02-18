# GlouGlouBot - Discord Bot

Discord bot with slash commands to send private notifications to a designated user.

## Features

- **Multi-language support**: English (default) and French
- **`/settarget`** (Admin): Set the user who will receive notifications
- **`/setcooldown`** (Admin): Configure cooldown duration
- **`/setlanguage`** (Admin): Set bot language (en/fr)
- **`/viewcooldown`**: Display current cooldown
- **`/deepthroat`** or **`/gorgeprofonde`**: Send a private notification to the target user

## Setup

### Prerequisites

- Python 3.8+
- Discord Developer account

### Installation

1. **Create Discord Application**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Enable these intents in the Bot section:
     - SERVER MEMBERS INTENT
     - MESSAGE CONTENT INTENT
   - Copy the bot token

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   - Create a `.env` file:
     ```
     DISCORD_TOKEN=your_token_here
     ```

4. **Invite bot to server**
   - In OAuth2 > URL Generator, select:
     - Scopes: `bot`, `applications.commands`
     - Permissions: Send Messages, Use Slash Commands, Read Messages

5. **Run the bot**
   ```bash
   python app.py
   ```

## Usage

1. Admin sets target: `/settarget @user`
2. Anyone can use: `/deepthroat` or `/gorgeprofonde`
3. Target receives a private message with details

## Configuration

- **Language**: `/setlanguage en` or `/setlanguage fr`
- **Cooldown**: `/setcooldown 60` (seconds)
- Settings are saved in `config.json`

## Technologies

- discord.py v2.3
- Python 3.8+
