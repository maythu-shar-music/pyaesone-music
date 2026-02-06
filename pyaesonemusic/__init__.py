from pyaesonemusic.core.bot import pisces
from pyaesonemusic.core.dir import dirr
from pyaesonemusic.core.git import git
from pyaesonemusic.core.userbot import Userbot
from pyaesonemusic.misc import dbb, heroku

from SafoneAPI import SafoneAPI
from .logging import LOGGER

dirr()
git()
dbb()
heroku()

app = pisces()
userbot = Userbot()
api = SafoneAPI()


from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()

APP = "myanmarmusic_4bot"  # connect music api key "Dont change it"
