import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
import datetime
import random
import os

# --- 1. SETUP: Replace these with your actual Role IDs from Discord ---
ROLE_MAP = {
    "Age": 1498429264897376306, 1498446891757600828,
    "Gender": 1498447053125193759, 1498447127930470471, 1498447330053980170
    "Gaming": 1498447507607519303, 1498447571700683024, 1498447635512819942, 1498447694367162378, 1498447748608036975, 1498447802051854399
}

import discord
from discord.ext import commands
from discord.ui import Button, View

# I've mapped your IDs here. 
# FEEL FREE TO RENAME THE LABELS (the text in quotes) to match your roles!
ROLE_MAP = {
    # Age Roles
    "minor": 1498429264897376306, 
    "legal": 1498446891757600828,
    
    # Gender Roles
    "male": 1498447053125193759, 
    "female": 1498447127930470471, 
    "non-binary": 1498447330053980170,
    
    # Gaming Roles
    "genshin": 1498447507607519303, 
    "minecraft": 1498447571700683024, 
    "roblox": 1498447635512819942, 
    "among us": 1498447694367162378, 
    "codm": 1498447748608036975, 
    "valo": 1498447802051854399
}

class RoleButton(Button):
    def __init__(self, label, role_id):
        super().__init__(label=label, style=discord.ButtonStyle.secondary, custom_id=f"role_{role_id}")
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        if not role:
            return await interaction.response.send_message("Role not found!", ephemeral=True)

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"Removed the **{role.name}** role!", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"Added the **{role.name}** role!", ephemeral=True)

class PersistentRoleView(View):
    def __init__(self):
        super().__init__(timeout=None)
        for name, r_id in ROLE_MAP.items():
            self.add_item(RoleButton(label=name, role_id=r_id))

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True 
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(PersistentRoleView())

bot = MyBot()

@bot.command()
@commands.has_permissions(administrator=True)
async def post_roles(ctx):
    """Run !post_roles in Discord to see the buttons"""
    await ctx.send("### 📋 Select Your Roles\nClick the buttons below to add or remove roles from your profile.", view=PersistentRoleView())

# --- 3. BOT CLASS SETUP ---
class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True          # For Welcome & Roles
        intents.message_content = True  # For !sync
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # This makes the buttons work even after the bot restarts on Railway
        self.add_view(PersistentRoleView())

bot = MyBot()

# --- 4. EVENTS (WELCOME) ---
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="welcome") or \
              discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        embed = discord.Embed(title="🌸 Welcome!", description=f"Hi {member.mention}!", color=0xffb6c1)
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

# --- 5. SYSTEM COMMANDS (SYNC) ---
@bot.command()
@commands.is_owner()
async def sync(ctx):
    try:
        bot.tree.copy_global_to(guild=ctx.guild)
        synced = await bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"✅ Synced {len(synced)} commands instantly!")
    except Exception as e:
        await ctx.send(f"❌ Sync failed: {e}")

@bot.command()
@commands.has_permissions(administrator=True)
async def post_roles(ctx):
    """Posts the button role message"""
    await ctx.send("Select your roles below:", view=PersistentRoleView())

# --- 6. MODERATION & FUN (SLASH COMMANDS) ---
@bot.tree.command(name="clear", description="Delete messages")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)
    await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"🗑️ Deleted {amount} messages.", ephemeral=True)

@bot.tree.command(name="mute", description="Mute a member (minutes)")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int):
    await member.timeout(datetime.timedelta(minutes=minutes))
    await interaction.response.send_message(f"🔇 Muted {member.display_name} for {minutes}m.")

@bot.tree.command(name="embed", description="Send a professional embed")
@app_commands.checks.has_permissions(manage_messages=True)
async def embed_cmd(interaction: discord.Interaction, title: str, description: str, image_url: str = None):
    e = discord.Embed(title=title, description=description, color=discord.Color.random())
    if image_url: e.set_image(url=image_url)
    await interaction.response.send_message("Sent!", ephemeral=True)
    await interaction.channel.send(embed=e)

# --- 7. RUN ---
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
