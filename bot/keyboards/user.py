from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async

from bot.handlers.utils import get_main_menu_button
from bot.keyboards.utils import add_back_button, build_pagination_button
from orders.models import Order
from products.models import Category, Product, SubCategory

ITEMS_PER_PAGE = 2


main_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Каталог', callback_data='category_page')],
        [InlineKeyboardButton(text='Корзина', callback_data='get_cart')],
        [InlineKeyboardButton(text='Мои заказы', callback_data='get_orders')],
        [InlineKeyboardButton(text='FAQ', callback_data='faq_page')]
    ]
)


async def get_categories_keyboard(page: int = 1) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    categories = await sync_to_async(list)(Category.objects.all())
    total = len(categories)

    if total == 0:
        await get_main_menu_button(builder)
        return builder.as_markup()

    offset = (page - 1) * ITEMS_PER_PAGE

    for category in categories[offset:offset+ITEMS_PER_PAGE]:
        builder.add(
            InlineKeyboardButton(
                text=category.name,
                callback_data=f'category_{category.id}_page_1'
            )
        )

    pagination = await build_pagination_button(
        page,
        offset,
        total,
        ITEMS_PER_PAGE,
        'category'
    )
    if pagination: builder.row(*pagination)

    await get_main_menu_button(builder)

    return builder.adjust(2).as_markup()


async def get_subcategories_keyboard(category_id: int, page: int = 1):
    builder = InlineKeyboardBuilder()
    offset = (page - 1) * ITEMS_PER_PAGE

    category = await (Category.objects.filter(id=category_id)
                      .prefetch_related('sub_categories')
                      .afirst())
    sub_categories = category.sub_categories.all()

    total = await sub_categories.acount()
    if total == 0:
        await add_back_button(builder, 'category', category_id)
        return builder.as_markup()
    for subcategory in sub_categories[offset:offset+ITEMS_PER_PAGE]:
        builder.add(
            InlineKeyboardButton(
                text=subcategory.name,
                callback_data=f'subcategory_{subcategory.id}_page_1'
            )
        )

    pagination = await build_pagination_button(
        page,
        offset,
        total,
        ITEMS_PER_PAGE,
        f'category_{category_id}'
    )
    if pagination: builder.row(*pagination)

    await add_back_button(builder, 'category', category_id)

    return builder.adjust(2).as_markup()


async def get_products_keyboard(subcategory_id: int, page: int = 1) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    offset = (page - 1) * ITEMS_PER_PAGE

    sub_category = await (SubCategory.objects.filter(id=subcategory_id)
                          .prefetch_related('products')
                          .select_related('category')
                          .afirst())
    products = sub_category.products.all()
    total = await products.acount()

    if total == 0:
        await add_back_button(builder, 'subcategory', sub_category.category.id)
        return builder.as_markup()

    for product in products[offset:offset+ITEMS_PER_PAGE]:
        builder.add(
            InlineKeyboardButton(
                text=product.name,
                callback_data=f'product_select_{product.id}'
            )
        )

    category_id = products[0].sub_category.category.id
    pagination = await build_pagination_button(
        page,
        offset,
        total,
        ITEMS_PER_PAGE,
        f'subcategory_{subcategory_id}'
    )
    if pagination: builder.row(*pagination)

    await add_back_button(builder, 'subcategory', category_id)

    return builder.adjust(2).as_markup()


async def get_product_keyboard(product: Product):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text='Добавить в корзину',
            callback_data=f'add_to_cart_{product.id}'
        )
    )
    await add_back_button(builder, 'products', product.sub_category.id)
    builder.add(
        InlineKeyboardButton(
            text='Корзина',
            callback_data=f'get_cart'
        )
    )
    return builder.adjust(2).as_markup()


async def get_quantity_keyboard(product: Product) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for i in range(1, 11):
        builder.add(InlineKeyboardButton(
            text=str(i),
            callback_data=f'add_to_cart_{product.id}_{i}'
        ))
    builder.add(InlineKeyboardButton(
        text='Назад',
        callback_data=f'product_select_{product.id}'
    ))
    return builder.adjust(5).as_markup()


async def remove_cart_item_keyboard(cart_item_id):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text='Удалить из корзины',
        callback_data=f'remove_cart_item_{cart_item_id}'
    ))
    return builder.adjust(2).as_markup()

async def remove_cart_item_quantity(cart_item):
    builder = InlineKeyboardBuilder()
    for i in range(1, cart_item.quantity):
        builder.add(InlineKeyboardButton(
            text=str(i),
            callback_data=f'remove_cart_item_{cart_item.id}_{i}'
        ))
    builder.add(InlineKeyboardButton(
        text='Все',
        callback_data=f'remove_cart_item_{cart_item.id}_{cart_item.quantity}'
    ))
    builder.add(InlineKeyboardButton(
        text='Назад',
        callback_data=f'get_cart'
    ))

    return builder.adjust(5).as_markup()

async def get_add_order_keyboard(items):
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.add(InlineKeyboardButton(text=f'Удалить {item.product.name}', callback_data=f'remove_cart_item_{item.id}'))

    builder.add(InlineKeyboardButton(text='Оформить заказ', callback_data='add_order'))
    await get_main_menu_button(builder)

    return builder.adjust(2).as_markup()


async def get_paid_keyboard(order, is_back=False):
    builder = InlineKeyboardBuilder()
    if not order.is_paid:
        builder.add(InlineKeyboardButton(
            text='Оплатить',
            callback_data=f'paid_{order.id}'
        ))
        builder.add(InlineKeyboardButton(
            text='Удалить заказ',
            callback_data=f'delete_order_{order.id}'
        ))

    if is_back:
        builder.add(InlineKeyboardButton(
            text='Назад',
            callback_data=f'get_orders'
        ))

    await get_main_menu_button(builder)

    return builder.adjust(2).as_markup()


async def get_orders_keyboard(orders):
    builder = InlineKeyboardBuilder()
    for order in orders:
        builder.add(InlineKeyboardButton(
            text=f'Заказ № {order.id} от {order.created_at.strftime("%d.%m.%Y")} {"Оплачен" if order.is_paid else "Не оплачен"}',
            callback_data=f'get_order_{order.id}'
        ))
    await get_main_menu_button(builder)

    return builder.adjust(1).as_markup()


async def get_pay_keyboard(order: Order):
    builder = InlineKeyboardBuilder()
    if not order.is_paid:
        builder.add(InlineKeyboardButton(text='СБП', callback_data=f'pay_sbp_{order.id}'))
    await get_main_menu_button(builder)
    return builder.adjust(1).as_markup()