from typing import Optional

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def build_pagination_button(
        page: int,
        offset: int,
        objects_count: int,
        items_per_page: int,
        prefix: str,
):
    """Возвращает кнопки Назад и Вперед для Инлайн клавиатуры"""
    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(
            InlineKeyboardButton(
                text='⬅️',
                callback_data=f'{prefix}_page_{page - 1}'
            )
        )

    if offset + items_per_page < objects_count:
        pagination_buttons.append(
            InlineKeyboardButton(
                text='➡️',
                callback_data=f'{prefix}_page_{page + 1}'
            )
        )

    return pagination_buttons

async def add_back_button(
        builder: InlineKeyboardBuilder,
        model_name: str,
        parent_id: Optional[int] = None
):
    """Добавляет кнопку Назад"""
    if not parent_id:
        return

    back_data = 'category_page_1'
    # if model_name == 'category':
    #     back_data = 'category_page_1'
    if model_name == 'subcategory':
        back_data = f'category_{parent_id}_page_1'
    elif model_name == 'products':
        back_data = f'subcategory_{parent_id}_page_1'
    ic(back_data)
    builder.row(
        InlineKeyboardButton(
            text='↩️ Назад',
            callback_data=back_data
        )
    )
