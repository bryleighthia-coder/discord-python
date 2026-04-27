import discord
from discord import app_commands
from discord.ext import commands
import datetime
import random
import os

# --- 1. SETUP & INTENTS ---
intents = discord.Intents.default()
intents.message_content = True  # For !sync
intents.members = True          # For Welcome & Moderation
bot = commands.Bot(command_prefix="!", intents=intents)

# --- 2. BUTTON ROLES SYSTEM ---
# These buttons persist even after the bot restarts
class RoleButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Member Role", style=discord.ButtonStyle.success, custom_id="role_member")
    async def member_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, name="Member") # Ensure this role exists!
        if not role:
            return await interaction.response.send_message("❌ Role 'Member' not found!", ephemeral=True)
        
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"❌ Removed {role.name} from you.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"✅ Added {role.name} to you!", ephemeral=True)

# --- 3. EVENTS (READY & WELCOME) ---
@bot.event
async def on_ready():
    bot.add_view(RoleButtonView()) # Essential for persistent buttons
    print(f"Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="welcome") or \
              discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        embed = discord.Embed(title="🌸 Welcome!", description=f"Hi {member.mention}! Welcome to {member.guild.name}!", color=0xffb6c1)
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

# --- 4. INSTANT SYNC ---
@bot.command()
@commands.is_owner()
async def sync(ctx):
    try:
        bot.tree.copy_global_to(guild=ctx.guild)
        synced = await bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"✅ Synced {len(synced)} commands instantly!")
    except Exception as e:
        await ctx.send(f"❌ Sync failed: {e}")

# --- 5. EMBEDS & MESSAGING ---
@bot.tree.command(name="embed", description="Send a professional embed")
@app_commands.checks.has_permissions(manage_messages=True)
async def embed_cmd(interaction: discord.Interaction, title: str, description: str, image_url: str = None):
    e = discord.Embed(title=title, description=description, color=discord.Color.random())
    if image_url: e.set_image(url=image_url)
    e.set_footer(text=f"Sent by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
    await interaction.response.send_message("Embed sent!", ephemeral=True)
    await interaction.channel.send(embed=e)

# --- 6. MODERATION ---
@bot.tree.command(name="clear", description="Purge messages")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"🗑️ Deleted {len(deleted)} messages.")

@bot.tree.command(name="kick", description="Kick a user")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "None"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"✅ Kicked {member.display_name}")

@bot.tree.command(name="mute", description="Mute a member (minutes)")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int):
    await member.timeout(datetime.timedelta(minutes=minutes))
    await interaction.response.send_message(f"🔇 Muted {member.display_name} for {minutes}m.")

# --- 7. INFO & FUN ---
@bot.tree.command(name="serverinfo", description="View server stats")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    e = discord.Embed(title=f"🏡 {guild.name}", color=discord.Color.blue())
    e.add_field(name="Members", value=guild.member_count)
    if guild.icon: e.set_thumbnail(url=guild.icon.url)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="hug", description="Hug someone!")
async def hug(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(f"💖 {interaction.user.mention} hugs {member.mention}!")

@bot.tree.command(name="button_roles", description="Setup button role message")
@app_commands.checks.has_permissions(manage_roles=True)
async def br(interaction: discord.Interaction):
    await interaction.response.send_message("Click below to get your roles:", view=RoleButtonView())

# --- 8. RUN BOT ---
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
