from aiogram.types import InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async

from bot.keyboards import user as kb
from orders.models import CartItem, TGUser
from utils.converter import to_rub


async def get_main_menu_button(builder: InlineKeyboardBuilder):
    builder.add(InlineKeyboardButton(text='Главное меню', callback_data='main_menu'))
