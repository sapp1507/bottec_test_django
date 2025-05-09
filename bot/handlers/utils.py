from aiogram.types import Message
from asgiref.sync import sync_to_async

from bot.keyboards import user as kb
from orders.models import CartItem, TGUser
from utils.converter import to_rub
