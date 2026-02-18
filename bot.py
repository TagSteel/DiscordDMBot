import discord
from discord import app_commands
from discord.ext import commands
import os
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta
import time
from translations import get_text, format_time

# Load environment variables
load_dotenv()

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Configuration file to store targets per server
CONFIG_FILE = 'config.json'

# Dictionary to store last command usage per server
# Format: {guild_id: timestamp}
last_usage = {}

def load_config():
    """Load configuration from JSON file"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    """Save configuration to JSON file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_target_user(guild_id):
    """Get the target user ID for a server"""
    config = load_config()
    guild_config = config.get(str(guild_id))
    if isinstance(guild_config, dict):
        return guild_config.get('target_user')
    return guild_config  # Old format (backward compatibility)

def set_target_user(guild_id, user_id):
    """Set the target user for a server"""
    config = load_config()
    if str(guild_id) not in config:
        config[str(guild_id)] = {}
    config[str(guild_id)]['target_user'] = user_id
    save_config(config)

def get_cooldown(guild_id):
    """Get the configured cooldown for a server (in seconds)"""
    config = load_config()
    guild_config = config.get(str(guild_id))
    if isinstance(guild_config, dict):
        return guild_config.get('cooldown', 60)  # 60 seconds by default
    return 60  # 60 seconds by default

def set_cooldown(guild_id, cooldown_seconds):
    """Set the cooldown for a server (in seconds)"""
    config = load_config()
    if str(guild_id) not in config:
        config[str(guild_id)] = {}
    elif not isinstance(config[str(guild_id)], dict):
        # Migration: convert old format (just ID) to new format
        old_target = config[str(guild_id)]
        config[str(guild_id)] = {'target_user': old_target}
    
    config[str(guild_id)]['cooldown'] = cooldown_seconds
    save_config(config)

def get_language(guild_id):
    """Get the configured language for a server"""
    config = load_config()
    guild_config = config.get(str(guild_id))
    if isinstance(guild_config, dict):
        return guild_config.get('language', 'en')  # English by default
    return 'en'  # English by default

def set_language(guild_id, language):
    """Set the language for a server"""
    config = load_config()
    if str(guild_id) not in config:
        config[str(guild_id)] = {}
    elif not isinstance(config[str(guild_id)], dict):
        # Migration: convert old format (just ID) to new format
        old_target = config[str(guild_id)]
        config[str(guild_id)] = {'target_user': old_target}
    
    config[str(guild_id)]['language'] = language
    save_config(config)

def check_cooldown(guild_id):
    """
    Check if the command can be used on the server
    Returns (can_use: bool, remaining_time: int)
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
    """Record the timestamp of the last usage for the server"""
    last_usage[guild_id] = time.time()

@bot.event
async def on_ready():
    """Event triggered when the bot is ready"""
    print(get_text(0, 'bot_connected', name=bot.user.name, id=bot.user.id))
    print('------')
    
    try:
        # Sync slash commands
        synced = await bot.tree.sync()
        print(get_text(0, 'commands_synced', count=len(synced)))
    except Exception as e:
        print(get_text(0, 'sync_error', error=e))

@bot.tree.command(name="settarget", description="Set the user who will receive notifications (Admin only)")
@app_commands.describe(user="The user who will receive the pings")
@app_commands.checks.has_permissions(administrator=True)
async def settarget(interaction: discord.Interaction, user: discord.Member):
    """
    Command to set the target user who will receive notifications
    Admin only
    """
    guild_id = interaction.guild.id
    set_target_user(guild_id, user.id)
    
    await interaction.response.send_message(
        get_text(guild_id, 'target_set', user=user.name),
        ephemeral=True
    )

@bot.tree.command(name="setcooldown", description="Set the cooldown for the /deepthroat command (Admin only)")
@app_commands.describe(seconds="Cooldown duration in seconds (minimum: 1, maximum: 86400)")
@app_commands.checks.has_permissions(administrator=True)
async def setcooldown(interaction: discord.Interaction, seconds: int):
    """
    Command to set the cooldown for the /deepthroat command
    Admin only
    """
    if seconds < 1:
        await interaction.response.send_message(
            get_text(interaction.guild.id, 'cooldown_min_error'),
            ephemeral=True
        )
        return
    
    if seconds > 86400:  # 24 hours max
        await interaction.response.send_message(
            get_text(interaction.guild.id, 'cooldown_max_error'),
            ephemeral=True
        )
        return
    
    guild_id = interaction.guild.id
    set_cooldown(guild_id, seconds)
    
    # Format time in a readable way
    time_str = format_time(seconds, guild_id)
    
    await interaction.response.send_message(
        get_text(guild_id, 'cooldown_set', time_str=time_str, seconds=seconds),
        ephemeral=True
    )

@bot.tree.command(name="viewcooldown", description="Display the current cooldown for the /deepthroat command")
async def viewcooldown(interaction: discord.Interaction):
    """
    Command to display the current configured cooldown for the server
    """
    guild_id = interaction.guild.id
    cooldown = get_cooldown(guild_id)
    
    # Format time in a readable way
    time_str = format_time(cooldown, guild_id)
    
    await interaction.response.send_message(
        get_text(guild_id, 'cooldown_current', time_str=time_str, seconds=cooldown),
        ephemeral=True
    )

@bot.tree.command(name="setlanguage", description="Set the bot language for this server (Admin only)")
@app_commands.describe(language="Language (en for English, fr for French)")
@app_commands.checks.has_permissions(administrator=True)
async def setlanguage(interaction: discord.Interaction, language: str):
    """
    Command to set the bot language for the server
    Admin only
    """
    language = language.lower()
    
    if language not in ['en', 'fr']:
        await interaction.response.send_message(
            get_text(interaction.guild.id, 'language_invalid'),
            ephemeral=True
        )
        return
    
    guild_id = interaction.guild.id
    set_language(guild_id, language)
    
    language_name = "English" if language == 'en' else "Français"
    
    await interaction.response.send_message(
        get_text(guild_id, 'language_set', language=language_name),
        ephemeral=True
    )

async def handle_notification_command(interaction: discord.Interaction):
    """
    Common handler for notification commands
    Sends a private message to the configured target user
    """
    author = interaction.user
    guild = interaction.guild
    channel = interaction.channel
    
    # Check cooldown (per server)
    can_use, remaining = check_cooldown(guild.id)
    if not can_use:
        # Format remaining time
        time_str = format_time(remaining, guild.id)
        
        await interaction.response.send_message(
            get_text(guild.id, 'cooldown_active', time_str=time_str),
            ephemeral=True
        )
        return
    
    # Get target user ID
    target_user_id = get_target_user(guild.id)
    
    if not target_user_id:
        await interaction.response.send_message(
            get_text(guild.id, 'no_target_set'),
            ephemeral=True
        )
        return
    
    # Get target user
    try:
        user = await guild.fetch_member(target_user_id)
    except discord.NotFound:
        await interaction.response.send_message(
            get_text(guild.id, 'target_not_found'),
            ephemeral=True
        )
        return
    
    try:
        # Create embed for the private message
        embed = discord.Embed(
            title=get_text(guild.id, 'mention_title'),
            description=get_text(guild.id, 'mention_description', author=author.name),
            color=discord.Color.blurple(),
            timestamp=datetime.now()
        )
        
        embed.add_field(name=get_text(guild.id, 'mention_server'), value=guild.name, inline=True)
        embed.add_field(name=get_text(guild.id, 'mention_channel'), value=f"#{channel.name}", inline=True)
        embed.add_field(name=get_text(guild.id, 'mention_by'), value=author.name, inline=False)
        embed.set_footer(text=f"{get_text(guild.id, 'mention_server')}: {guild.name}")
        
        # Send private message to target user
        await user.send(embed=embed)
        
        # Record command usage for the server
        set_last_usage(guild.id)
        
        # Confirm in the channel (visible to everyone)
        await interaction.response.send_message(
            get_text(guild.id, 'mention_success', author=author.name, target=user.name)
        )
        
    except discord.Forbidden:
        # User has disabled private messages
        await interaction.response.send_message(
            get_text(guild.id, 'dm_forbidden', user=user.name)
        )
    except Exception as e:
        # Other error
        print(f"Error sending private message: {e}")
        await interaction.response.send_message(
            get_text(guild.id, 'general_error')
        )

@bot.tree.command(name="deepthroat", description="Send a private notification to the target user")
async def deepthroat(interaction: discord.Interaction):
    """
    Slash command that sends a private message to the configured target user
    (English version)
    """
    await handle_notification_command(interaction)

@bot.tree.command(name="gorgeprofonde", description="Envoie une notification privée à l'utilisateur cible")
async def gorgeprofonde(interaction: discord.Interaction):
    """
    Slash command that sends a private message to the configured target user
    (French version)
    """
    await handle_notification_command(interaction)

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        print("❌ ERROR: Discord token is not defined in the .env file")
        exit(1)
    
    bot.run(token)
