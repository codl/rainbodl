import tweepy
import yaml
import os
import random
from PIL import Image, ImageColor
import tempfile

CONF_FILE = os.path.expanduser('~/.rainbodl')

def get_conf():
    try:
        with open(CONF_FILE, 'r') as f:
            return yaml.safe_load(f)
    except Exception:
        set_conf({"consumer_key": "FILL ME IN", "consumer_secret": "FILL ME IN", "image": "FILL ME IN"})
        print("Please edit %s to include your app's API keys" % CONF_FILE)
        exit(1)

def set_conf(conf):
    try:
        with open(CONF_FILE, 'w') as f:
            yaml.dump(conf, f, default_flow_style=False)
    except Exception as e:
        print(e)
        #print("Couldn't write to %s" % CONF_FILE)

def auth_dance(conf):
    auth = tweepy.OAuthHandler(conf['consumer_key'], conf['consumer_secret'])
    url = auth.get_authorization_url()
    print("Please go to %s and accept, then paste the authorization code here." % url)
    code = input("Authorization code:")
    try:
        auth.get_access_token(code)
        conf['access_token'] = auth.access_token
        conf['access_token_secret'] = auth.access_token_secret
        set_conf(conf)
        return conf
    except tweepy.TweepError:
        print("Something went awry. Try again soon.")
        exit(2)

def make_profile_picture(conf, filename):
    im = Image.open(os.path.expanduser(conf["image"]))
    im = im.convert(mode="RGBA")

    size = im.size
    color = ImageColor.getrgb("hsl(%s,100%%,45%%)" % (random.randint(0, 360),))

    background = Image.new("RGBA", size, color)

    final = Image.alpha_composite(background, im)

    final.save(filename)

if __name__ == "__main__":
    conf = get_conf()
    if('access_token' not in conf or 'access_token_secret' not in conf):
        conf = auth_dance(conf)
    auth = tweepy.OAuthHandler(conf['consumer_key'], conf['consumer_secret'])
    auth.set_access_token(conf['access_token'], conf['access_token_secret'])
    api = tweepy.API(auth)


    handle, filename = tempfile.mkstemp(suffix='.png')

    make_profile_picture(conf, filename)

    try:
        api.update_profile_image(filename)
    except Exception as e:
        print(dir(e.response.content))

    os.unlink(filename)

