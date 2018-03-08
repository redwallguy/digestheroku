import discord
import asyncio
import time
import os

discToken = os.environ.get('DISCORD_TOKEN')
comm_chan_id = int(os.environ.get('COMMANDS_CHANNEL_ID'))

client = discord.Client()

@client.event
async def on_ready():
    while True:
        print("Sending ping")
        channel = client.get_channel(comm_chan_id)
        await channel.send("!resetSpam")
        disTrue = await asyncio.sleep(5,result=True)
        if disTrue:
            pass

client.run(discToken)
