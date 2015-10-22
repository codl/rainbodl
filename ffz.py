import requests
import random
import tweepy
from PIL import Image, ImageDraw
from io import BytesIO
from tempfile import mkstemp
import os

FFZ_API = 'https://api.frankerfacez.com/'
FFZ_EMOTE_URL = 'http://www.frankerfacez.com/emoticons/{}'

USER_AGENT = "rainbodl (https://github.com/codl/rainbodl)"
HEADERS = {'User-Agent': USER_AGENT}

BG_COLOURS = ("#f2f2f2", "#19191f")

IMAGE_SIZE = (262, 136)

def get_random_ffz():
    r = requests.get(FFZ_API + 'v1/emoticons', headers=HEADERS)
    num_pages = r.json()['_pages']
    page = random.randint(1, num_pages)
    r = requests.get(FFZ_API + 'v1/emoticons', params={'page': page}, headers=HEADERS)
    emote = random.choice(r.json()['emoticons'])

    max_multiplier = 4 if '4' in emote['urls'] else 2 if '2' in emote['urls'] else 1

    url = emote['urls'][str(max_multiplier)]
    if url[:2] == '//':
        url = "https:" + url

    return { 'url': url, 'multiplier': max_multiplier, 'id': emote['id'], 'name': emote['name'] }

def make_pic(ffz):
    # set up background
    im = Image.new("RGBA", (IMAGE_SIZE[0] * ffz['multiplier'], IMAGE_SIZE[1] * ffz['multiplier']), BG_COLOURS[0])
    draw = ImageDraw.Draw(im)
    draw.rectangle([im.size[0]//2, 0, im.size[0], im.size[1]], fill=BG_COLOURS[1])
    del draw

    # get the emote
    req = requests.get(ffz["url"], headers=HEADERS);
    emote = Image.open(BytesIO(req.content))

    if emote.mode != "RGBA":
        emote = emote.convert("RGBA")

    # paste it on
    try:
        im.paste(emote, ( im.size[0]//4 - emote.size[0]//2, im.size[1]//2 - emote.size[1]//2 ), emote)
        im.paste(emote, ( 3 * im.size[0]//4 - emote.size[0]//2, im.size[1]//2 - emote.size[1]//2 ), emote)
    except ValueError as e:
        print("fucked up if true!!!")
        print(ffz)
        raise e

    return im


def tweet(api):

    ffz = get_random_ffz()
    im = make_pic(ffz)

    descriptor, filename = mkstemp(suffix='.png')
    f = open(descriptor, 'w+b')

    im.save(f, 'PNG')

    url = FFZ_EMOTE_URL.format(ffz['id'])
    name = ffz['name']

    try:
        media = api.media_upload(filename);
        api.update_status(media_ids=[media.media_id,], status="{} {}".format(name, url));
    except tweepy.TweepError as e:
        print(e.with_traceback())
        exit(1)

    f.close()
    os.unlink(filename)
