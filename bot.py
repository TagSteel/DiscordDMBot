import discord
from discord import app_commands
from discord.ext import commands
import os
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta
import time

# Charger les variables d'environnement
load_dotenv()

# Configuration du bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Fichier de configuration pour stocker les cibles par serveur
CONFIG_FILE = 'config.json'

# Dictionnaire pour stocker les dernières utilisations de la commande par serveur
# Format: {guild_id: timestamp}
last_usage = {}

def load_config():
    """Charge la configuration depuis le fichier JSON"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    """Sauvegarde la configuration dans le fichier JSON"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_target_user(guild_id):
    """Récupère l'ID de l'utilisateur cible pour un serveur"""
    config = load_config()
    guild_config = config.get(str(guild_id))
    if isinstance(guild_config, dict):
        return guild_config.get('target_user')
    return guild_config  # Ancien format (compatibilité)

def set_target_user(guild_id, user_id):
    """Définit l'utilisateur cible pour un serveur"""
    config = load_config()
    if str(guild_id) not in config:
        config[str(guild_id)] = {}
    config[str(guild_id)]['target_user'] = user_id
    save_config(config)

def get_cooldown(guild_id):
    """Récupère le cooldown configuré pour un serveur (en secondes)"""
    config = load_config()
    guild_config = config.get(str(guild_id))
    if isinstance(guild_config, dict):
        return guild_config.get('cooldown', 60)  # 60 secondes par défaut
    return 60  # 60 secondes par défaut

def set_cooldown(guild_id, cooldown_seconds):
    """Définit le cooldown pour un serveur (en secondes)"""
    config = load_config()
    if str(guild_id) not in config:
        config[str(guild_id)] = {}
    elif not isinstance(config[str(guild_id)], dict):
        # Migration: convertir l'ancien format (juste l'ID) en nouveau format
        old_target = config[str(guild_id)]
        config[str(guild_id)] = {'target_user': old_target}
    
    config[str(guild_id)]['cooldown'] = cooldown_seconds
    save_config(config)

def check_cooldown(guild_id):
    """
    Vérifie si la commande peut être utilisée sur le serveur
    Retourne (can_use: bool, remaining_time: int)
    """
    cooldown_seconds = get_cooldown(guild_id)
    
    if guild_id not in last_usage:
        return True, 0
    
    last_time = last_usage[guild_id]
    elapsed = time.time() - last_time
    
    if elapsed >= cooldown_seconds:
        return True, 0
    
    remaining = int(cooldown_seconds - elapsed)
    return False, remaining

def set_last_usage(guild_id):
    """Enregistre le timestamp de la dernière utilisation pour le serveur"""
    last_usage[guild_id] = time.time()

@bot.event
async def on_ready():
    """Événement déclenché quand le bot est prêt"""
    print(f'✅ Bot connecté en tant que {bot.user.name} (ID: {bot.user.id})')
    print('------')
    
    try:
        # Synchroniser les commandes slash
        synced = await bot.tree.sync()
        print(f'✅ {len(synced)} commande(s) slash synchronisée(s)')
    except Exception as e:
        print(f'❌ Erreur lors de la synchronisation des commandes: {e}')

@bot.tree.command(name="setcible", description="Définir l'utilisateur qui recevra les notifications (Admin seulement)")
@app_commands.describe(utilisateur="L'utilisateur qui recevra les pings")
@app_commands.checks.has_permissions(administrator=True)
async def setcible(interaction: discord.Interaction, utilisateur: discord.Member):
    """
    Commande pour définir l'utilisateur cible qui recevra les notifications
    Réservée aux administrateurs
    """
    guild_id = interaction.guild.id
    set_target_user(guild_id, utilisateur.id)
    
    await interaction.response.send_message(
        f"✅ **{utilisateur.name}** est maintenant défini comme cible pour la commande /gorgeprofonde !",
        ephemeral=True
    )

@bot.tree.command(name="setcooldown", description="Définir le cooldown de la commande /gorgeprofonde (Admin seulement)")
@app_commands.describe(secondes="Durée du cooldown en secondes (minimum: 1, maximum: 86400)")
@app_commands.checks.has_permissions(administrator=True)
async def setcooldown(interaction: discord.Interaction, secondes: int):
    """
    Commande pour définir le cooldown de la commande /gorgeprofonde
    Réservée aux administrateurs
    """
    if secondes < 1:
        await interaction.response.send_message(
            "❌ Le cooldown doit être d'au moins 1 seconde.",
            ephemeral=True
        )
        return
    
    if secondes > 86400:  # 24 heures max
        await interaction.response.send_message(
            "❌ Le cooldown ne peut pas dépasser 86400 secondes (24 heures).",
            ephemeral=True
        )
        return
    
    guild_id = interaction.guild.id
    set_cooldown(guild_id, secondes)
    
    # Formater le temps de manière lisible
    if secondes < 60:
        time_str = f"{secondes} seconde(s)"
    elif secondes < 3600:
        minutes = secondes // 60
        secs = secondes % 60
        time_str = f"{minutes} minute(s)" + (f" et {secs} seconde(s)" if secs > 0 else "")
    else:
        hours = secondes // 3600
        minutes = (secondes % 3600) // 60
        time_str = f"{hours} heure(s)" + (f" et {minutes} minute(s)" if minutes > 0 else "")
    
    await interaction.response.send_message(
        f"✅ Le cooldown de la commande /gorgeprofonde est maintenant de **{time_str}** ({secondes}s).",
        ephemeral=True
    )

@bot.tree.command(name="viewcooldown", description="Afficher le cooldown actuel de la commande /gorgeprofonde")
async def viewcooldown(interaction: discord.Interaction):
    """
    Commande pour afficher le cooldown actuel configuré pour le serveur
    """
    guild_id = interaction.guild.id
    cooldown = get_cooldown(guild_id)
    
    # Formater le temps de manière lisible
    if cooldown < 60:
        time_str = f"{cooldown} seconde(s)"
    elif cooldown < 3600:
        minutes = cooldown // 60
        secs = cooldown % 60
        time_str = f"{minutes} minute(s)" + (f" et {secs} seconde(s)" if secs > 0 else "")
    else:
        hours = cooldown // 3600
        minutes = (cooldown % 3600) // 60
        time_str = f"{hours} heure(s)" + (f" et {minutes} minute(s)" if minutes > 0 else "")
    
    await interaction.response.send_message(
        f"⏱️ Le cooldown actuel pour /gorgeprofonde est de **{time_str}** ({cooldown}s).",
        ephemeral=True
    )

@bot.tree.command(name="gorgeprofonde", description="Envoie une notification privée à l'utilisateur cible")
async def gorgeprofonde(interaction: discord.Interaction):
    """
    Commande slash qui envoie un message privé à l'utilisateur cible configuré
    pour l'informer qu'il a été pingé
    """
    author = interaction.user
    guild = interaction.guild
    channel = interaction.channel
    
    # Vérifier le cooldown (par serveur)
    can_use, remaining = check_cooldown(guild.id)
    if not can_use:
        # Formater le temps restant
        if remaining < 60:
            time_str = f"{remaining} seconde(s)"
        elif remaining < 3600:
            minutes = remaining // 60
            secs = remaining % 60
            time_str = f"{minutes} minute(s)" + (f" et {secs} seconde(s)" if secs > 0 else "")
        else:
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            time_str = f"{hours} heure(s)" + (f" et {minutes} minute(s)" if minutes > 0 else "")
        
        await interaction.response.send_message(
            f"⏱️ Cette commande est en cooldown pour le serveur. Attendez encore **{time_str}** avant de l'utiliser à nouveau.",
            ephemeral=True
        )
        return
    
    # Récupérer l'ID de l'utilisateur cible
    target_user_id = get_target_user(guild.id)
    
    if not target_user_id:
        await interaction.response.send_message(
            "❌ Aucune cible n'a été définie pour ce serveur. Un administrateur doit utiliser `/setcible` d'abord.",
            ephemeral=True
        )
        return
    
    # Récupérer l'utilisateur cible
    try:
        utilisateur = await guild.fetch_member(target_user_id)
    except discord.NotFound:
        await interaction.response.send_message(
            "❌ L'utilisateur cible n'est plus sur ce serveur. Un administrateur doit redéfinir la cible avec `/setcible`.",
            ephemeral=True
        )
        return
    
    try:
        # Créer un embed pour le message privé
        embed = discord.Embed(
            title="📬 Vous avez été mentionné !",
            description=f"**{author.name}** vous a pingé via /gorgeprofonde",
            color=discord.Color.blurple(),
            timestamp=datetime.now()
        )
        
        embed.add_field(name="🏠 Serveur", value=guild.name, inline=True)
        embed.add_field(name="💬 Salon", value=f"#{channel.name}", inline=True)
        embed.add_field(name="👤 Par", value=author.name, inline=False)
        embed.set_footer(text=f"Serveur: {guild.name}")
        
        # Envoyer le message privé à l'utilisateur ciblé
        await utilisateur.send(embed=embed)
        
        # Enregistrer l'utilisation de la commande pour le serveur
        set_last_usage(guild.id)
        
        # Confirmer dans le salon (visible par tous)
        await interaction.response.send_message(
            f"✅ **{author.name}** a pingé **{utilisateur.name}** via /gorgeprofonde ! 📬"
        )
        
    except discord.Forbidden:
        # L'utilisateur a désactivé les messages privés
        await interaction.response.send_message(
            f"❌ Impossible d'envoyer un message privé à **{utilisateur.name}**. "
            f"L'utilisateur a peut-être désactivé les messages privés."
        )
    except Exception as e:
        # Autre erreur
        print(f"Erreur lors de l'envoi du message privé: {e}")
        await interaction.response.send_message(
            f"❌ Une erreur s'est produite lors de l'envoi du message."
        )

# Lancer le bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        print("❌ ERREUR: Le token Discord n'est pas défini dans le fichier .env")
        exit(1)
    
    bot.run(token)
