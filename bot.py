import discord
from discord import app_commands
from discord.ext import commands
import random

# --- BOT SETUP ---
intents = discord.Intents.default()
intents.message_content = True # Needed for prefix commands like !sync
bot = commands.Bot(command_prefix="!", intents=intents)

# --- SLASH COMMANDS ---

# 1. Echo Command (Repeat after me)
@bot.tree.command(name="echo", description="Repeats your message")
async def echo(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(f"Bot says: {message}")

# 2. Roll Command (Random number)
@bot.tree.command(name="roll", description="Roll a dice (default 1-6)")
async def roll(interaction: discord.Interaction, max_num: int = 6):
    result = random.randint(1, max_num)
    await interaction.response.send_message(f"🎲 You rolled a {result}!")

# 3. Avatar Command (See someone's profile picture)
@bot.tree.command(name="avatar", description="Get a user's avatar")
async def avatar(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    await interaction.response.send_message(member.display_avatar.url)

# 4. Clear Command (Moderation - Delete messages)
@bot.tree.command(name="clear", description="Delete a number of messages")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True) # "Bot is thinking..."
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"Successfully deleted {len(deleted)} messages.", ephemeral=True)

# --- THE SYNC COMMAND (IMPORTANT) ---
# Type !sync in your server to make these new commands show up in the / menu
@bot.command()
@commands.is_owner()
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("Commands synced globally! (May take up to an hour to appear everywhere)")

# --- RUN THE BOT ---
import os
bot.run(os.getenv('DISCORD_TOKEN'))
