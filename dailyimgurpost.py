import imgurpackage
import praw
import datetime
import redis
import os

red_cid = os.environ.get('REDDIT_CLIENT_ID')
red_csecret = os.environ.get('REDDIT_CLIENT_SECRET')
red_pass = os.environ.get('REDDIT_PASSWORD')
red_uname = os.environ.get('REDDIT_USERNAME')

r = redis.from_url(os.environ.get("REDIS_URL"))
subs_list = r.lrange("meme_subs",0,-1)

def get_top_reddit(subs_list):
    reddit = praw.Reddit(client_id=red_cid,
                     client_secret=red_csecret,
                     password=red_pass,
                     user_agent='Meme scraper by u/'+red_uname,
                     username=red_uname)

    subreddits = []
    for sub in subs_list:
        subreddits.append(reddit.subreddit(sub))

    postUrls = {}

    for subreddit in subreddits:
        for submission in subreddit.hot(limit=5):
            if submission.stickied == False and (datetime.datetime.now() - datetime.datetime.fromtimestamp(submission.created_utc)).total_seconds() < 86400:
                postUrls[subreddit.display_name] = [submission.url,submission.title]
                break
    for key in postUrls:
        print(postUrls[key])
    return postUrls

imgurpackage.postToImgur(get_top_reddit(subs))
