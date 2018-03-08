import discord
import asyncio
import os
import errormail
import redis

client = discord.Client()

discToken = os.environ.get('DISCORD_TOKEN')
r = redis.from_url(os.environ.get("REDIS_URL"))

ign_channels = [int(x) for x in r.lrange("ign_channels",0,-1)]

@client.event
async def on_ready():
    for guild in client.guilds:
        for tch in guild.text_channels:
            if tch.id not in ign_channels:
                await tch.send("IT'S HIGH NOON'")
                await channel.send(imgurpackage.get_digest())
    keylist = r.keys("*/requests")
    reqMsg = ""
    for key in keylist:
        reqMsg += "Requests from " + key.replace(r"/requests$","")
        reqMsg += ":\n"
        for req in r.lrange(key,0,-1):
            reqMsg += req + "\n"
        reqMsg += "-----------------------------------------------------\n"
        r.delete(key)
    if reqMsg != "":
        errormail.sendDevError("Requests", reqMsg)

client.start(discToken)
client.close()
