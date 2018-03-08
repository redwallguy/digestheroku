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

bot = commands.Bot(command_prefix='!!')
r = redis.from_url(os.environ.get("REDIS_URL"))
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

async def botChannel(ctx):
    return ctx.channel.id == comm_chan_id

                
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
aysnc def notBanned(ctx):
    if ctx.author.id in banlist:
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
        
@bot.event
async def on_command(ctx):
    if  ctx.author.id != bot.user.id:
        if ctx.author.id not in spam_dict:
            spam_dict[ctx.author.id] = 1
        else:
            spam_dict[ctx.author.id] += 1
            if spam_dict[ctx.author.id] > 5:
                spam_dict[ctx.author.id] = 5

def flushTempBan():
    spam_dict = {}

@bot.command()
@commands.check(botChannel)
async def resetSpam(ctx):
    flushTempBan()

#-----------------------------------------------------------
# Bot commands (Administrative)
#-----------------------------------------------------------

@bot.command()
@commands.check(isAdmin)
async def makeMod(ctx,uid):
    if uid not in mods:
        r.lpush("discord_mods",uid)
        mods.append(uid)
        await ctx.send("Come, and dine with gods.")
        return True
    else:
        return False

@bot.command()
@commands.check(isAdmin)
async def delMod(ctx,uid):
    if uid in mods:
        r.lrem("discord_mods", uid)
        mods.remove(uid)
        await ctx.send("How the mighty have fallen...")
        return True
    else:
        return False

@bot.command()
@commands.check(isMod)
async def ban(ctx,uid):
    if uid not in mods and uid not in banlist:
        r.lpush("banlist", uid)
        banlist.append(uid)
        await ctx.send("Begone!")
        return True
    else:
        return False

@bot.command()
@commands.check(isMod)
async def unban(ctx,uid):
    if uid in banlist:
        r.lrem("banlist", uid)
        banlist.remove(uid)
        await ctx.send("Welcome back, child.")
        return True
    else:
        return False

#-----------------------------------------------------------
# Bot commands (General)
#-----------------------------------------------------------

@bot.command()
async def gtr(ctx, *subs):
    mToSend = ""
    for sub in subs:
        mToSend += sub + ': 'get_top_reddit(sub) + '\n'
    await ctx.send(mToSend)

@bot.command()
async def request(ctx, *, req):
    userReqLen = r.llen(str(ctx.user.id)+'/requests')
    if userReqLen < 5:
        r.lpush(str(ctx.user.id)+'/requests', req)
        await ctx.send("Request acknowledged.")
    else:
        await ctx.send("Daily request limit reached. Requests reset at 7:00 EST.")

@bot.command()
async def digest(ctx, *args):
    if len(args) == 0:
        await ctx.send(imgurpackage.get_digest())
    else:
        await ctx.send(imgurpackage.get_digest(args[0]))

@bot.command()
@commands.check(isMod)
async def addSub(ctx, sub):
    if sub_exists(sub) and sub not in subs_list:
        subs_list.append(sub)
        r.lpush("meme_subs", sub)
        await ctx.send("Subreddit added.")
        return True
    else:
        return False

@bot.command()
@commands.check(isMod)
async def delSub(ctx, sub):
    if sub in subs_list:
        subs_list.remove(sub)
        r.lrem("meme_subs", sub)
        await ctx.send("Subreddit removed".)
        return True
    else:
        return False
#-----------------------------------------------------------
# Run bot
#-----------------------------------------------------------

bot.run(discToken)
