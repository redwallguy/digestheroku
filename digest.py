import discord
from discord.ext import commands
import requests
import praw
import asyncio
import imgurpackage
import errormail
from prawcore import NotFound
import os
import redis

#-----------------------------------------------------------
# Variable imports and client initializations
#-----------------------------------------------------------
discToken = os.environ.get('DISCORD_TOKEN')
red_cid = os.environ.get('REDDIT_CLIENT_ID')
red_csecret = os.environ.get('REDDIT_CLIENT_SECRET')
red_pass = os.environ.get('REDDIT_PASSWORD')
red_uname = os.environ.get('REDDIT_USERNAME')
comm_chan_id = os.environ.get('COMMANDS_CHANNEL_ID')

bot = commands.Bot(command_prefix='!')
r = redis.from_url(os.environ.get("REDIS_URL"), decode_responses=True)
reddit = praw.Reddit(client_id=red_cid,
                     client_secret=red_csecret,
                     password=red_pass,
                     user_agent='Meme scraper by u/'+red_uname,
                     username=red_uname)

subs_list = r.lrange("meme_subs",0,-1)
overlord = int(r.get("discord_admin"))
mods = [int(x) for x in r.lrange("discord_mods",0,-1)]
banlist = [int(x) for x in r.lrange("banlist",0,-1)]

spam_dict = {}


#-----------------------------------------------------------
# Helper functions and checks
#-----------------------------------------------------------

def getSubs():
    return subs_list

async def isMod(ctx):
    if ctx.author.id in mods or ctx.author.id == overlord:
        return True
    else:
        return False

async def isAdmin(ctx):
    return ctx.author.id == overlord

def sub_exists(sub):
    exists = True
    try:
        reddit.subreddits.search_by_name(sub, exact=True)
    except NotFound:
        exists = False
    return exists
                
def get_top_reddit(sub):
    if sub_exists(sub):
        subreddit = reddit.subreddit(sub)
        for submission in subreddit.hot(limit=5):
            if submission.stickied == False:
                url = (submission.url)
                break
        return url
    else:
        return "Nonexistant subreddit"

#-----------------------------------------------------------
# Spam prevention
#-----------------------------------------------------------
@bot.check
async def notBanned(ctx):
    if ctx.author.id in banlist and ctx.author.id != overlord:
        return False
    else:
        return True

@bot.check
async def stopSpamming(ctx):
    if ctx.author.id == overlord:
        return True
    else:
        if ctx.author.id in spam_dict:
            if spam_dict[ctx.author.id] == 5:
                return False
        return True
        
@bot.event
async def on_command(ctx):
    if ctx.author.id not in spam_dict:
        spam_dict[ctx.author.id] = 1
    else:
        spam_dict[ctx.author.id] += 1
        if spam_dict[ctx.author.id] > 5:
            spam_dict[ctx.author.id] = 5

def flushTempBan():
    global spam_dict = {}

@bot.event
async def on_ready():
    while True:
        flushTempBan()
        await asyncio.sleep(5)

#-----------------------------------------------------------
# Bot commands (Administrative)
#-----------------------------------------------------------

@bot.command()
@commands.check(isAdmin)
async def makeMod(ctx,member: discord.Member):
    """
    Promote member to mod.
    Only usable by [REDACTED]
    """
    uid = member.id
    if uid not in mods:
        r.lpush("discord_mods",uid)
        mods.append(uid)
        await ctx.send("Come, and dine with gods.")
        return True
    else:
        return False

@bot.command()
@commands.check(isAdmin)
async def delMod(ctx,member: discord.Member):
    """
    Remove mod powers from member.
    Only usable by [REDACTED]
    """
    uid = member.id
    if uid in mods:
        r.lrem("discord_mods", uid)
        mods.remove(uid)
        await ctx.send("How the mighty have fallen...")
        return True
    else:
        return False

@bot.command()
@commands.check(isMod)
async def ban(ctx, member: discord.Member):
    """
    Ban member.
    Only usable by mods.
    """
    uid = member.id
    if uid not in mods and uid not in banlist and uid != overlord:
        r.lpush("banlist", uid)
        banlist.append(uid)
        await ctx.send("Begone!")
        return True
    else:
        return False

@bot.command()
@commands.check(isMod)
async def unban(ctx,member: discord.Member):
    """
    Unban member.
    Only usable by mods.
    """
    uid = member.id
    if uid in banlist:
        r.lrem("banlist", uid)
        banlist.remove(uid)
        await ctx.send("Welcome back, child.")
        return True
    else:
        return False

@bot.command()
async def getMods(ctx):
    """
    Display list of mods.
    """
    modmsg = "These are your current rulers of the Digest:\n"\
             "-------------------------------------------\n"
    for mod in mods:
        modmem = await bot.get_user_info(mod)
        modmsg += modmem.name + "\n"
    await ctx.send(modmsg)

@bot.command()
async def getBannedOnes(ctx):
    """
    Display list of banned members.
    """
    banmsg = "These are the exiles. Look upon them and weep.\n"\
             "----------------------------------------------\n"
    for banppl in banlist:
        banmem = await bot.get_user_info(banppl)
        banmsg += banmem.name + "\n"
    await ctx.send(banmsg)
#-----------------------------------------------------------
# Bot commands (General)
#-----------------------------------------------------------

@bot.command()
async def gtr(ctx, *subs):
    """
    Returns the top post of sub(s) requested.

    Maximum limit per request is 10 subreddits.
    """
    if len(subs) > 10:
        raise commands.TooManyArguments()
    mToSend = ""
    for sub in subs:
        mToSend += sub + ': ' + get_top_reddit(sub) + '\n'
    await ctx.send(mToSend)

@bot.command()
async def request(ctx, *, req):
    """
    Adds message to your daily request queue.

    At high noon, requests are sent to Dev$ and the queue reset.
    """
    userReqLen = r.llen(str(ctx.author)+'/requests')
    if userReqLen < 5:
        r.lpush(str(ctx.author)+'/requests', req)
        await ctx.send("Request acknowledged.")
    else:
        await ctx.send("Daily request limit reached. Requests reset at 7:00 EST.")

@bot.command()
async def digest(ctx, vol: int =-1):
    """
    Returns requested version of the Digest.
    
    No arguments gives the current Digest.
    An integer argument will give the requested version of the Digest, if it
    exists.
    """
    if vol < 0:
        await ctx.send(imgurpackage.get_digest())
    else:
        await ctx.send(imgurpackage.get_digest(str(vol)))

@bot.command(ignore_extra=False)
@commands.check(isMod)
async def addSub(ctx, sub):
    """
    Adds subreddit to the Digest.
    Only usable by mods.
    """
    if sub_exists(sub) and sub not in subs_list:
        subs_list.append(sub)
        r.lpush("meme_subs", sub)
        await ctx.send("Subreddit added.")
        return True
    else:
        return False

@bot.command(ignore_extra=False)
@commands.check(isMod)
async def delSub(ctx, sub):
    """
    Removes subreddit from the Digest.
    Only usable by mods.
    """
    if sub in subs_list:
        subs_list.remove(sub)
        r.lrem("meme_subs", sub)
        await ctx.send("Subreddit removed.")
        return True
    else:
        return False

@bot.command(aliases=['sublist','listsubs','ls'])
async def listSubs(ctx):
    """
    Lists subreddits currently in the Digest.
    """
    subs = getSubs()
    submsg = "Subs in the Digest are:\n"
    for sub in subs:
        submsg += sub + "\n"
    await ctx.send(submsg)
#-----------------------------------------------------------
# Error handlers
#-----------------------------------------------------------
@gtr.error
async def gtr_error(ctx,error):
    if isinstance(error, commands.TooManyArguments):
        await ctx.send("Woah there, cowboy. 10 subs or less at a time.")

@addSub.error
async def addsub_error(ctx,error):
    if isinstance(error, commands.TooManyArguments):
        await ctx.send("One sub at a time")

@delSub.error
async def delsub_error(ctx,error):
    if isinstance(error, commands.TooManyArguments):
        await ctx.send("One sub at a time")
#-----------------------------------------------------------
# Run bot
#-----------------------------------------------------------

bot.run(discToken)
