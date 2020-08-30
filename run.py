import os
from dotenv import load_dotenv

from discord_key_bot import bot
from discord_key_bot.keyparse import parse_key


load_dotenv()

bot.run(os.environ["TOKEN"])
