import discord
from discord import app_commands
from discord.ext import commands
import os

# 1. SETUP: Enable necessary permissions
intents = discord.Intents.default()
intents.message_content = True  # Required to read the !sync command
bot = commands.Bot(command_prefix="!", intents=intents)

# 2. INSTANT SYNC COMMAND: Type !sync in your server to push updates
@bot.command()
@commands.is_owner() # Only you can run this
async def sync(ctx):
    try:
        # Syncs specifically to the server you're in for INSTANT results
        bot.tree.copy_global_to(guild=ctx.guild)
        synced = await bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"✅ Success! Synced {len(synced)} commands to this server instantly.")
    except Exception as e:
        await ctx.send(f"❌ Sync failed: {e}")

# 3. EXAMPLE COMMANDS
@bot.tree.command(name="ping", description="Check bot speed")
async def ping(interaction: discord.Interaction):
    # Always use 'response.send_message' for the FIRST reply
    await interaction.response.send_message(f"🏓 Pong! Latency: {round(bot.latency * 1000)}ms")

@bot.tree.command(name="echo", description="Bot repeats your words")
async def echo(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(f"You said: {message}")

@bot.tree.command(name="clear", description="Deletes messages (Requires Manage Messages)")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    # DEFER prevents the "application did not respond" error for slow tasks
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"🗑️ Deleted {len(deleted)} messages.", ephemeral=True)

# 4. RUN: Railway automatically provides the token via Environment Variables
token = os.getenv('DISCORD_TOKEN')
if token:
    bot.run(token)
else:
    print("CRITICAL ERROR: 'DISCORD_TOKEN' variable not found in Railway settings!")
