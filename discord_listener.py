import discord
import os



intents = discord.Intents(messages=True, guilds=True)
intents.message_content = True
intents.guild_messages = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    else:
        # Process message, check for valid json, clean it up if necessary, write to database
        pass

client.run(token=os.getenv("DISCORD_BOT_TOKEN"))
