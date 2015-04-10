import tweepy
import yaml
import os
from pgmagick import Image, CompositeOperator, Color, ColorHSL, Geometry
import random
from ctypes import cast, POINTER

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

def make_profile_picture(conf):
    image = Image(os.path.expanduser(conf["image"]))

    size = Geometry(image.columns(), image.rows())
    color = "hsl(%s,255,255)" % (random.randint(0, 255),)
    color = "green"
    background = Image(size, Color)

    background.composite(image, 0, 0, CompositeOperator.OverCompositeOp)
    background.write("/tmp/bah.png")

if __name__ == "__main__":
    conf = get_conf()
    if('access_token' not in conf or 'access_token_secret' not in conf):
        conf = auth_dance(conf)
    auth = tweepy.OAuthHandler(conf['consumer_key'], conf['consumer_secret'])
    auth.set_access_token(conf['access_token'], conf['access_token_secret'])
    api = tweepy.API(auth)


    try:
        api.update_status("this is a test")
    except Exception as e:
        print(dir(e.response.content))

