from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

TOKEN = getenv('BOT_TOKEN')
GROUP_CHAT_ID = getenv('GROUP_CHAT_ID')

storage = MemoryStorage()
dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
