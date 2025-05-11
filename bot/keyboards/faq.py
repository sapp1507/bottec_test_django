from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async

from bot.handlers.utils import get_main_menu_button
from bot.keyboards.utils import build_pagination_button, add_back_button
from faq.models import FAQCategory, FAQItem

ITEMS_PER_PAGE = 2

async def get_faq_category_keyboard(page):
    builder = InlineKeyboardBuilder()
    offset = (page - 1) * ITEMS_PER_PAGE
    faq_category = await sync_to_async(list)(
        FAQCategory.objects
        .prefetch_related('faq_items')
        .all()
    )
    total = len(faq_category)

    builder.add(InlineKeyboardButton(text='Задать свой вопрос', callback_data='add_faq'))

    if total != 0:
        for category in faq_category[offset:offset+ITEMS_PER_PAGE]:
            builder.add(InlineKeyboardButton(text=category.name, callback_data=f'faq_category_{category.id}'))

    pagination = await build_pagination_button(
        page,
        offset,
        total,
        ITEMS_PER_PAGE,
        'faq'
    )
    if pagination: builder.row(*pagination)

    await get_main_menu_button(builder)
    return builder.adjust(1).as_markup()


async def get_faq_items_keyboard(category_id, page):
    builder = InlineKeyboardBuilder()
    offset = (page - 1) * ITEMS_PER_PAGE

    items = await sync_to_async(list)(
        FAQItem.objects.filter(
            category_id=category_id,
            is_active=True,
            answer__isnull=False
        )
    )
    total = len(items)
    if total == 0:
        await add_back_button(
            builder,
            model_name='faq',
            parent_id=category_id
        )
        return builder.as_markup()

    for item in items[offset:offset+ITEMS_PER_PAGE]:
        builder.add(InlineKeyboardButton(text=item.question, callback_data=f'faq_item_{item.id}'))

    pagination = await build_pagination_button(
        page,
        offset,
        total,
        ITEMS_PER_PAGE,
        f'faq_category_{category_id}'
    )
    if pagination: builder.row(*pagination)
    await add_back_button(
        builder,
        model_name='faq',
        parent_id=category_id
    )
    await get_main_menu_button(builder)
    return builder.adjust(1).as_markup()
