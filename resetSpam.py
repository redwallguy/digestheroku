import discord
import asyncio
import time
import os

discToken = os.environ.get('DISCORD_TOKEN')
comm_chan_id = os.environ.get('COMMANDS_CHANNEL_ID')

client = discord.Client()

@client.event
async def on_ready():
    channel = client.get_channel(comm_chan_id)
    channel.send("!!resetSpam")

while True:
    client.start(discToken)
    client.close()
    time.sleep(5)
