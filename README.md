# rainbodl: a crash course in bad twitter bot

first off: don't use this

if you must use this, here's how:

## setting up

Make sure you have python and pip installed.

Register an app with twitter at https://apps.twitter.com/ and take note of the consumer key and consumer secret values.

```
pip install -r requirements.txt
python rainbodl.py auth
```

It will give you the location of your config file and ask you to fill in your consumer key and secret.

Once that's done:

```
python rainbodl.py auth # again, yep
```

Follow instructions to give the bot access to your account. You're set up! Congratulations!

## commands

all of these commands except ffz-png will add a config block when run without config, which must be filled in

no output means success

put these in a crontab to run them on a schedule

### rainbodl

*the original command*

```
python rainbodl.py rainbodl
```

changes avatar to the specified image or a random image from the specified directory

the image will be overlaid on a random coloured background, so any transparent parts will let the background show.
if change_profile_color is set to true in the config (the default), the profile colour will be set to that same colour.

### post-image

```
python rainbodl.py post-image
```

uploads a random image from a directory. an accompanying status can be specified in the config

### post-status

```
python rainbodl.py post-status
```

posts a random status (or media!) from a file

by default tweets are separated by a single newline, this can be changed in the config if multiline tweets are desired

tweets starting with | denote a media upload, for example a file containing

```
|hellorbs/1.gif
|hellorbs/2.gif
|hellorbs/3.gif
```

will upload one of these three files at random

it probably works with video too i haven't tried it. report back if you do

### post-ffz

```
python rainbodl.py post-ffz
```

posts a random emote from FrankerFaceZ. see [@ffz_png](https://twitter.com/ffz_png)

this command doesn't require any config 

### auth

```
python rainbodl.py auth
```

checks if all of the api keys and access tokens and whatnot are in order.

## it doesnt work and you suck

file an issue on github or bother me on twitter [@codl](https://twitter.com/codl)
