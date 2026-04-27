import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
import datetime
import random
import os

# --- 1. SETUP: YOUR ROLE ID MAP ---
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

# --- 2. PERSISTENT BUTTONS (ID BASED) ---
class RoleButton(Button):
    def __init__(self, label, role_id):
        super().__init__(label=label, style=discord.ButtonStyle.secondary, custom_id=f"role_{role_id}")
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        if not role:
            return await interaction.response.send_message("❌ Role not found! Check IDs.", ephemeral=True)
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"Removed **{role.name}**!", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"Added **{role.name}**!", ephemeral=True)

class PersistentRoleView(View):
    def __init__(self):
        super().__init__(timeout=None)
        for name, r_id in ROLE_MAP.items():
            self.add_item(RoleButton(label=name, role_id=r_id))

# --- 3. PERSISTENT BUTTON (NAME BASED - FOR MEMBER ROLE) ---
class RoleButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Get Member Role", style=discord.ButtonStyle.primary, custom_id="role_member")
    async def member_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, name="Member") 
        if not role:
            return await interaction.response.send_message("❌ Role 'Member' not found!", ephemeral=True)
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"❌ Removed {role.name}", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"✅ Added {role.name}", ephemeral=True)

# --- 4. BOT CLASS SETUP ---
class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True          # For Welcome & Roles
        intents.message_content = True  # For ! commands
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # This allows buttons to work forever after a restart
        self.add_view(PersistentRoleView())
        self.add_view(RoleButtonView())

bot = MyBot()

# --- 5. EVENTS & WELCOME ---
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="welcome") or \
              discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        embed = discord.Embed(title="🌸 Welcome!", description=f"Hi {member.mention}! Welcome to {member.guild.name}!", color=0xffb6c1)
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

# --- 6. SYSTEM COMMANDS ---
@bot.command()
@commands.is_owner()
async def sync(ctx):
    bot.tree.copy_global_to(guild=ctx.guild)
    synced = await bot.tree.sync(guild=ctx.guild)
    await ctx.send(f"✅ Synced {len(synced)} commands instantly!")

@bot.command()
@commands.has_permissions(administrator=True)
async def post_roles(ctx):
    """Posts your Age/Gender/Game role buttons"""
    await ctx.send("### 📋 Select Your Roles", view=PersistentRoleView())

@bot.tree.command(name="button_roles", description="Post the Member role button")
@app_commands.checks.has_permissions(manage_roles=True)
async def rr(interaction: discord.Interaction):
    await interaction.response.send_message("Click below for the Member role!", view=RoleButtonView())

# --- 7. MODERATION & UTILITY ---
@bot.tree.command(name="clear", description="Purge messages")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)
    await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"🗑️ Deleted {amount} messages.", ephemeral=True)

@bot.tree.command(name="embed", description="Send a custom embed box")
@app_commands.checks.has_permissions(manage_messages=True)
async def embed_cmd(interaction: discord.Interaction, title: str, description: str, image_url: str = None):
    e = discord.Embed(title=title, description=description, color=discord.Color.random())
    if image_url: e.set_image(url=image_url)
    await interaction.response.send_message("Sent!", ephemeral=True)
    await interaction.channel.send(embed=e)

# --- 8. RUN THE BOT ---
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
