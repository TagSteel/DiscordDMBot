import discord
from discord import app_commands
from discord.ext import commands
import os
import json
from dotenv import load_dotenv
from datetime import datetime

# Charger les variables d'environnement
load_dotenv()

# Configuration du bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Fichier de configuration pour stocker les cibles par serveur
CONFIG_FILE = 'config.json'

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
    return config.get(str(guild_id))

def set_target_user(guild_id, user_id):
    """Définit l'utilisateur cible pour un serveur"""
    config = load_config()
    config[str(guild_id)] = user_id
    save_config(config)

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

@bot.tree.command(name="gorgeprofonde", description="Envoie une notification privée à l'utilisateur cible")
async def gorgeprofonde(interaction: discord.Interaction):
    """
    Commande slash qui envoie un message privé à l'utilisateur cible configuré
    pour l'informer qu'il a été pingé
    """
    author = interaction.user
    guild = interaction.guild
    channel = interaction.channel
    
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
