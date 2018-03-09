import redis
import os
import errormail
import json

r = redis.from_url(os.environ.get("REDIS_URL"), decode_responses=True)

subsstr = json.dumps(r.lrange("meme_subs",0,-1))
modsstr = json.dumps(r.lrange("discord_mods",0,-1))
banstr = json.dumps(r.lrange("banlist",0,-1))
volstr = r.get("digest_vol")
ignstr = json.dumps(r.lrange("ign_channels",0,-1))
errormail.sendDevError("Values backup", "Subs: " + subsstr +
                       "\nMods: " + modsstr + "\nBans: " +
                       banstr + "\nVol: " + volstr + "\nIgnore: " +
                       ignstr)

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
