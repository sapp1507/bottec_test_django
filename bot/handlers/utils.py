from aiogram.types import Message
from asgiref.sync import sync_to_async

from orders.models import TGUser, CartItem
from utils.converter import to_rub
from bot.keyboards import user as kb
