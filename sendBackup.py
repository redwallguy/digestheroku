import redis
import os
import errormail

r = redis.from_url(os.environ.get("REDIS_URL"))

subsstr = json.dumps(r.lrange("meme_subs",0,-1))
modsstr = json.dumps(r.lrange("discord_mods",0,-1))
banstr = json.dumps(r.lrange("banlist",0,-1))
volstr = r.get("digest_vol")
ignstr = json.dumps(r.lrange("ign_channels",0,-1))
errormail.sendDevError("Values backup", "Subs: " + subsstr +
                       "\nMods: " + modsstr + "\nBans: " +
                       banstr + "\nVol: " + volstr + "\nIgnore: " +
                       ignstr)
