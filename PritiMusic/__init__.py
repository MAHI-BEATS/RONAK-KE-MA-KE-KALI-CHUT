from PritiMusic.core.bot import Lucky
from PritiMusic.core.dir import dirr
from PritiMusic.core.git import git
from PritiMusic.core.userbot import Userbot
from PritiMusic.misc import dbb, heroku
from pyrogram import Client
from SafoneAPI import SafoneAPI
from .logging import LOGGER

dirr()
# git() # बोट को 'fatal: could not read Username' एरर और क्रैश से बचाने के लिए इसे बंद कर दिया है।
dbb()
heroku()

app = Lucky()
api = SafoneAPI()
userbot = Userbot()

from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
