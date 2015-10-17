import argparse
import os
import random
import stat
import sys
import tempfile
import tweepy
import yaml
from PIL import Image, ImageColor

import ffz


class ConfNotValid(Exception):
    pass

def get_conf():
    try:
        with open(conf_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception:
        return {}

def set_conf(module, conf):
    try:
        with open(conf_file, 'a+') as f:
            f.seek(0)
            orig_conf = yaml.safe_load(f)
            if not orig_conf:
                orig_conf = {}
            orig_conf[module] = conf
            f.seek(0)
            f.truncate()
            yaml.dump(orig_conf, f, default_flow_style=False, default_style='"')
    except Exception as e:
        print(e)

def auth_dance():
    try:
        conf = expect_conf("twitter", {"consumer_key": None, "consumer_secret": None})
    except ConfNotValid:
        print("Please fill in your API key and secret in %s" % (conf_file,), file=sys.stderr)
        exit(1)
    auth = tweepy.OAuthHandler(conf['consumer_key'], conf['consumer_secret'])
    url = auth.get_authorization_url()
    print("Please go to %s and accept, then paste the authorization code here." % url)
    code = input("Authorization code:")
    try:
        auth.get_access_token(code)
        conf['access_token'] = auth.access_token
        conf['access_token_secret'] = auth.access_token_secret
        set_conf('twitter', conf)
        return conf
    except tweepy.TweepError:
        print("Something went awry. Try again soon.")
        exit(2)

def expect_conf(module, values):
    conf = get_conf()

    valid = True
    if module not in conf:
        valid = False
        conf[module] = dict()

    for key in values:
        if key not in conf[module] or conf[module][key] == "FILL ME IN":
            if values[key] != None:
                conf[module][key] = values[key]
            else:
                valid = False
                conf[module][key] = "FILL ME IN"

    if not valid:
        set_conf(module, conf[module])
        raise ConfNotValid()
    else:
        return conf[module]

def rgb_tuple_to_hex(color):
    return '#%02X%02X%02X' % color

def rainbodl(api):
    try:
        conf = expect_conf("rainbodl", {"path": None, "change_profile_color": True})
    except ConfNotValid:
        print("Please fill in the location of the image(s) in %s" % (conf_file,), file=sys.stderr)
        exit(1)

    sourcefile = os.path.expanduser(conf['path'])
    if(stat.S_ISDIR(os.stat(sourcefile).st_mode)):
        sourcefile += os.sep + random.choice(os.listdir(sourcefile))

    _, filename = tempfile.mkstemp(suffix='.png')

    im = Image.open(sourcefile)
    im = im.convert(mode="RGBA")

    size = im.size
    hue = random.randint(0, 360);
    avcolor = ImageColor.getrgb("hsl(%s,100%%,70%%)" % (hue,))
    linkcolor = ImageColor.getrgb("hsl(%s,100%%,40%%)" % (hue,))

    background = Image.new("RGBA", size, avcolor)

    final = Image.alpha_composite(background, im)

    final.save(filename)

    api.update_profile_image(filename)

    if conf['change_profile_color']:
        api.update_profile(profile_link_color=rgb_tuple_to_hex(linkcolor))

    os.unlink(filename)

def post_image(api):
    try:
        conf = expect_conf("post_image", {"directory": None, "message": ""})
    except ConfNotValid:
        print("Please fill in the location of the image directory in %s" % (conf_file,), file=sys.stderr)
        exit(1)

    files = os.listdir(conf["directory"])
    filename = conf["directory"] + os.sep + random.choice(files)

    try:
        media = api.media_upload(filename);
        api.update_status(media_ids=[media.media_id,], status=conf["message"]);
    except tweepy.TweepError as e:
        print(e.with_traceback())
        exit(1)

def post_status(api):
    try:
        conf = expect_conf("post_status", {"path": None, "separator": "\n"})
    except ConfNotValid:
        print("Please fill in the location of the image directory in %s" % (conf_file,), file=sys.stderr)
        exit(1)

    with open(conf['path'], 'r') as f:
        statuses = f.read().split(conf['separator'])

    status = random.choice(statuses)

    api.update_status(status=status)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help="set the config file path", default="~/.rainbodl")
    parser.add_argument('command', choices={'auth', 'rainbodl', 'post-image', 'post-status', 'post-ffz'})
    args = parser.parse_args()

    global conf_file
    conf_file = os.path.expanduser(args.config)

    try:
        conf = expect_conf("twitter", {'access_token': None, 'access_token_secret': None})
    except ConfNotValid:
        conf = auth_dance()
    auth = tweepy.OAuthHandler(conf['consumer_key'], conf['consumer_secret'])
    auth.set_access_token(conf['access_token'], conf['access_token_secret'])
    api = tweepy.API(auth)

    if args.command == 'rainbodl':
        rainbodl(api)
    if args.command == 'post-image':
        post_image(api)
    if args.command == 'post-status':
        post_status(api)
    if args.command == 'post-ffz':
        ffz.tweet(api)
