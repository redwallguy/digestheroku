import imgurpython
import errormail
import asyncio
import traceback
import os
import redis

imgur_cid = os.environ.get('IMGUR_CLIENT_ID')
imgur_rtoken = os.environ.get('IMGUR_REFRESH_TOKEN')
imgur_csecret = os.environ.get('IMGUR_CLIENT_SECRET')

r = redis.from_url(os.environ.get("REDIS_URL"))
digest_vol = r.get("digest_vol")

def postToImgur(urls):
    try:
        imgurclient = imgurpython.ImgurClient(client_id=imgur_cid,
                                              client_secret=imgur_csecret,
                                              refesh_token=imgur_rtoken)
        title = "Meme Digest Vol. " + digest_vol
        album_info = imgurclient.create_album({"title": title})
        deletehash = album_info['deletehash']
        album_id = album_info['id']

        for key in urls:
            try:
                imgurclient.upload_from_url(urls[key][0],
                                            {"album":deletehash,
                                             "description":
                                             urls[key][1] + "\n-" +key})
            except:
                pass

        album_url = "imgur.com/a/" + album_id
        r.incr("digest_vol")
        return album_url
    except imgurpython.helpers.error.ImgurClientError as e:
        errormail.sendDevError("Imgur Error in script"
                               + os.path.basename(sys.argv[0]),
                               str(e.error_message))

def get_digest(vol_no = None):
    try:
        imgurclient = imgurpython.ImgurClient(client_id=imgur_cid,
                                              client_secret=imgur_csecret,
                                              refesh_token=imgur_rtoken)
        if vol_no is None:
            all_albums = imgurclient.get_account_albums("me", page=0)
            for album in all_albums:
                if "Meme Digest Vol." in album.title:
                    return album.link
        else:
            title = "Meme Digest Vol. " + vol_no
            count = 0
            while count <= int(imgurclient.get_account_album_count("me")/50):
                all_albums = imgurclient.get_account_albums("me", page=count)
                for album in all_albums:
                    if title == album.title:
                        return album.link
                count += 1
            return "Sorry, that volume is not yet made."
    except imgurpython.helpers.error.ImgurClientError as e:
        errormail.sendDevError("Imgur Error in script"
                               + os.path.basename(sys.argv[0]),
                               str(e.error_message))
