import discord
from discord import app_commands
from discord.ext import commands
import datetime
import random
import os

# --- 1. SETUP & INTENTS ---
intents = discord.Intents.default()
intents.message_content = True  # To read the !sync command
intents.members = True          # To see who joins and for moderation
bot = commands.Bot(command_prefix="!", intents=intents)

# --- 2. THE SYNC COMMAND (INSTANT UPDATE) ---
@bot.command()
@commands.is_owner()
async def sync(ctx):
    try:
        bot.tree.copy_global_to(guild=ctx.guild)
        synced = await bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"✅ Success! Synced {len(synced)} commands to this server instantly.")
    except Exception as e:
        await ctx.send(f"❌ Sync failed: {e}")

# --- 3. AUTO-WELCOME (MIMU STYLE) ---
@bot.event
async def on_member_join(member):
    # This looks for a channel named 'welcome' or 'general'
    channel = discord.utils.get(member.guild.text_channels, name="welcome") or \
              discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        embed = discord.Embed(
            title="🌸 New Friend!",
            description=f"Welcome to the server, {member.mention}! We're so happy you're here!",
            color=discord.Color.from_rgb(255, 182, 193)
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

# --- 4. SERVER & USER INFO (CARL-BOT STYLE) ---
@bot.tree.command(name="serverinfo", description="See server details")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"🏡 {guild.name}", color=discord.Color.blue())
    embed.add_field(name="Owner", value=guild.owner, inline=True)
    embed.add_field(name="Members", value=guild.member_count, inline=True)
    embed.add_field(name="Created", value=guild.created_at.strftime("%b %d, %Y"), inline=True)
    if guild.icon: embed.set_thumbnail(url=guild.icon.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="userinfo", description="See user details")
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    embed = discord.Embed(title=f"👤 {target.name}", color=target.color)
    embed.add_field(name="Joined Server", value=target.joined_at.strftime("%b %d, %Y"), inline=True)
    embed.set_thumbnail(url=target.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# --- 5. MODERATION & MANAGEMENT ---
@bot.tree.command(name="clear", description="Delete messages")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"🗑️ Deleted {len(deleted)} messages.")

@bot.tree.command(name="kick", description="Kick a member")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "None"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"✅ Kicked {member.display_name}")

@bot.tree.command(name="mute", description="Mute a member (minutes)")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int):
    await member.timeout(datetime.timedelta(minutes=minutes))
    await interaction.response.send_message(f"🔇 Muted {member.display_name} for {minutes}m.")

@bot.tree.command(name="create_role", description="Create a new role")
@app_commands.checks.has_permissions(manage_roles=True)
async def create_role(interaction: discord.Interaction, name: str, color_hex: str = "ffffff"):
    color = int(color_hex.replace("#", ""), 16)
    await interaction.guild.create_role(name=name, color=discord.Color(color))
    await interaction.response.send_message(f"✅ Created role: {name}")

# --- 6. MESSAGING & FUN ---
@bot.tree.command(name="embed", description="Send a custom embed box")
@app_commands.checks.has_permissions(manage_messages=True)
async def embed_cmd(interaction: discord.Interaction, title: str, description: str):
    e = discord.Embed(title=title, description=description, color=discord.Color.random())
    await interaction.response.send_message("Sent!", ephemeral=True)
    await interaction.channel.send(embed=e)

@bot.tree.command(name="hug", description="Hug someone!")
async def hug(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(f"💖 {interaction.user.mention} gives {member.mention} a big hug!")

@bot.tree.command(name="coinflip", description="Flip a coin")
async def coinflip(interaction: discord.Interaction):
    await interaction.response.send_message(f"🪙 It's **{random.choice(['Heads', 'Tails'])}**!")

# --- 7. START BOT ---
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
