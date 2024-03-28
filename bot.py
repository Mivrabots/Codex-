import discord
from discord.ext import commands
import sqlite3
from datetime import timedelta
import os

TOKEN = os.environ['TOKEN']



intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True

# create the bot instance
bot = commands.Bot(command_prefix='!', intents=intents)
#bot is ready/stated
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

#bot staus
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="game"))


# Connect to SQLite database
conn = sqlite3.connect('events.db')
c = conn.cursor()

# Create events table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS events
             (name TEXT, date TEXT, time TEXT, description TEXT, organizer TEXT, rsvps INTEGER, category TEXT)''')
conn.commit()

# Command to create a new event
@bot.command()
async def create_event(ctx, name, date, time, description):
    event_details = {
        'name': name,
        'date': date,
        'time': time,
        'description': description,
        'organizer': ctx.author.name,
        'rsvps': 0,
        'category': ''
    }
    c.execute("INSERT INTO events (name, date, time, description, organizer, rsvps, category) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (name, date, time, description, ctx.author.name, 0, ''))
    conn.commit()
    await ctx.send(f'Event "{name}" created!')

# Command to list all events
@bot.command()
async def list_events(ctx):
    c.execute("SELECT name FROM events")
    event_list = '\n'.join([row[0] for row in c.fetchall()])
    await ctx.send(f'**Events:**\n{event_list}')

# Command to get details of a specific event
@bot.command()
async def event_details(ctx, name):
    c.execute("SELECT * FROM events WHERE name=?", (name,))
    event = c.fetchone()
    if event:
        details = f'''**Name:** {event[0]}
**Date:** {event[1]}
**Time:** {event[2]}
**Description:** {event[3]}
**Organizer:** {event[4]}
**RSVPs:** {event[5]}
**Category:** {event[6]}'''
        await ctx.send(details)
    else:
        await ctx.send('Event not found!')

# Command to delete an event
@bot.command()
async def delete_event(ctx, name):
    c.execute("DELETE FROM events WHERE name=?", (name,))
    conn.commit()
    await ctx.send(f'Event "{name}" deleted!')

# Command to update event details
@bot.command()
async def update_event(ctx, name, field, value):
    if field.lower() in ['name', 'date', 'time', 'description', 'category']:
        c.execute(f"UPDATE events SET {field.lower()}=? WHERE name=?", (value, name))
        conn.commit()
        await ctx.send(f'Event "{name}" {field.lower()} updated to "{value}"!')
    else:
        await ctx.send('Invalid field. Available fields: name, date, time, description, category')

# Command to search for events by keyword
@bot.command()
async def search_events(ctx, keyword):
    c.execute("SELECT name FROM events WHERE description LIKE ?", ('%' + keyword + '%',))
    event_list = '\n'.join([row[0] for row in c.fetchall()])
    if event_list:
        await ctx.send(f'**Events matching "{keyword}":**\n{event_list}')
    else:
        await ctx.send('No events found matching the keyword.')

# Command to display upcoming events
@bot.command()
async def upcoming_events(ctx, num=5):
    c.execute("SELECT name, date FROM events ORDER BY date LIMIT ?", (num,))
    upcoming_events = '\n'.join([f'{row[0]} - {row[1]}' for row in c.fetchall()])
    await ctx.send(f'**Upcoming Events:**\n{upcoming_events}')

# Command to clear all events (for admins)
@bot.command()
@commands.has_permissions(administrator=True)
async def clear_events(ctx):
    c.execute("DELETE FROM events")
    conn.commit()
    await ctx.send('All events cleared!')

# Error handling for clear_events command
@clear_events.error
async def clear_events_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You don't have permission to use this command.")

# Command to view organizer's events
@bot.command()
async def my_events(ctx):
    c.execute("SELECT name FROM events WHERE organizer=?", (ctx.author.name,))
    user_events = '\n'.join([row[0] for row in c.fetchall()])
    if user_events:
        await ctx.send(f'**Your Events:**\n{user_events}')
    else:
        await ctx.send("You haven't organized any events yet.")

# Command to get help about EventMaster commands
@bot.command()
async def event_help(ctx):
    help_text = '''
**EventMaster Commands:**
- !create_event [name] [date] [time] [description]: Create a new event.
- !list_events: List all scheduled events.
- !event_details [name]: Get details of a specific event.
- !delete_event [name]: Delete an event (for admins).
- !update_event [name] [field] [value]: Update event details (for admins).
- !search_events [keyword]: Search for events by keyword.
- !upcoming_events [num]: Display upcoming events (default: 5).
- !clear_events: Clear all events (for admins).
- !my_events: View events organized by you.
- !event_help: Display this help message.
'''
    await ctx.send(help_text)


@bot.command()
async def announce(ctx, *, message):
    # Check if the user invoking the command is the bot owner
    if ctx.author.id == 719648115639975946:
        # Create an embed for the announcement
        embed = discord.Embed(title="Developer Announcement", description=message, color=0x00ff00)
        embed.set_footer(text="Sent by the bot owner")

        # Iterate over all guilds where the bot is a member
        for guild in bot.guilds:
            # Find a channel where the bot has permission to send messages
            channel = discord.utils.get(guild.text_channels, name="announcements")
            if channel is not None:
                # Send the announcement message as an embed to the channel
                await channel.send(embed=embed)
            else:
                # If there's no announcements channel, send to the first available text channel
                await guild.text_channels[0].send(embed=embed)
        await ctx.send("Announcement sent to all servers.")
    else:
        await ctx.send("You do not have permission to use this command.")




# Run the bot
bot.run(TOKEN)
