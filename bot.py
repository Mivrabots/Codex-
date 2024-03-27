
import discord
from discord.ext import commands
import os
import random
import asyncio

token = os.getenv('TOKEN')

# Define the intents
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True

# Set the prefix for commands
bot = commands.Bot(command_prefix='!', intents=intents)
developers = [719648115639975946, 1049825040998350918] 
# Define your commands and event handlers as before
@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello, {ctx.author.mention}!')

@bot.command()
async def support(ctx):
    invite_link = "https://discord.gg/dewSNCvS8S"  # Replace with your actual server invite link
    await ctx.send(f"Click [here](<{invite_link}>) to join our server. We will be there for you anytime.")


@bot.command()
async def invite(ctx):
    invite_link = "https://discord.com/oauth2/authorize?client_id=1222586427875921930&permissions=8&scope=bot"  # Replace with your actual bot invite link
    await ctx.send(f"Click [here](<{invite_link}>) to invite me to your server")
  
   
#moderation commands
@bot.command()
async def kick(ctx, member: discord.Member, *, reason):
    if ctx.author.guild_permissions.kick_members:
        await member.kick(reason=reason)
        await ctx.send(f'{member.mention} has been kicked for {reason}.')
    else:
        await ctx.send("You don't have permission to kick members.")

@bot.command()
async def ban(ctx, member: discord.Member, *, reason):
    if ctx.author.guild_permissions.ban_members:
        await member.ban(reason=reason)
        await ctx.send(f'{member.mention} has been banned for {reason}.')
    else:
        await ctx.send("You don't have permission to ban members.")

@bot.command()
async def unban(ctx, *, member):
    if ctx.author.guild_permissions.ban_members:
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'{user.mention} has been unbanned.')
                return
    else:
        await ctx.send("You don't have permission to unban members.")
#ttimeout
@bot.command()
async def mute(ctx, member: discord.Member, duration: int, *, reason):
    if ctx.author.guild_permissions.manage_roles:
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False)

        await member.add_roles(muted_role, reason=reason)
        await ctx.send(f'{member.mention} has been muted for {duration} seconds. Reason: {reason}')
        await asyncio.sleep(duration)
        await member.remove_roles(muted_role)
        await ctx.send(f'{member.mention} has been unmuted.')
    else:
        await ctx.send("You don't have permission to mute members.")


  
    
  








@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="made with ❤️"))


@bot.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            invite_link = "https://discord.gg/dewSNCvS8S"  # Replace with your support server invite link
            await channel.send("Thank you for inviting me! You can join the support server [here](<" + invite_link + ">)")
        break











# Run the bot with the token
bot.run(token)
