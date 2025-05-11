from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (CallbackQuery, FSInputFile, InlineKeyboardButton,
                           Message)

from bot.keyboards import user as kb
from bot.states.user import OrderStates
from orders.models import Cart, CartItem, Order, OrderItem, TGUser
from products.models import Product
from utils.converter import to_rub

router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Привет! Выбери пункт меню.',
                         reply_markup=kb.main_keyboard)


@router.callback_query(F.data.startswith('main_menu'))
async def main_menu(callback: CallbackQuery):
    await callback.message.answer(
        'Привет! Выбери пункт меню.',
        reply_markup=kb.main_keyboard
    )
    await callback.message.delete()


@router.callback_query(F.data.startswith('get_cart'))
async def get_cart(callback: CallbackQuery):
    user_id = callback.message.from_user.id if not callback.message.from_user.is_bot else callback.message.chat.id
    user = await TGUser.objects.filter(user_id=user_id).prefetch_related('cart__items__product').afirst()
    items = user.cart.items.all()
    total_price = 0
    message_answer = ''
    if not items:
        await callback.message.answer(
            'Корзина пуста',
            reply_markup=kb.main_keyboard
        )
        await callback.message.delete()
        return
    for item in items:
        total_price += item.price
        message_answer = message_answer + (
            f'=====   <b>{item.product.name}</b>   =====\n\n'
            f'{item.product.description}\n\n'
            f'Цена: {to_rub(item.product.price)}р.\n'
            f'Количество: {item.quantity}\n'
            f'Итого: {to_rub(item.price)} р.\n\n\n'
        )

    message_answer = message_answer + (
            '<b>Общая сумма: ' + to_rub(total_price) + 'р.</b>'
    )
    await callback.message.answer(
        message_answer,
        reply_markup=await kb.get_add_order_keyboard(items)
    )
    await callback.message.delete()





@router.callback_query(F.data.startswith('get_orders'))
async def get_orders_callback(callback: CallbackQuery):
    user_id = callback.message.from_user.id if not callback.message.from_user.is_bot else callback.message.chat.id
    user = await TGUser.objects.filter(user_id=user_id).prefetch_related('orders__items__product').afirst()
    orders = user.orders.all()
    await callback.message.answer(
        'Список заказов',
        reply_markup=await kb.get_orders_keyboard(orders)
    )
    await callback.message.delete()


@router.callback_query(F.data.startswith('category_page'))
async def get_category(callback: CallbackQuery):
    params = callback.data.split('_')
    page = 1
    if len(params) == 3:
        page = int(callback.data.split('_')[2])
    await callback.message.answer(
        'Выбери категорию:',
        reply_markup= await kb.get_categories_keyboard(page)
    )
    await callback.message.delete()


@router.callback_query(F.data.startswith('category_'))
async def get_subcategory(callback: CallbackQuery):
    params = callback.data.split('_')
    category_id = int(params[1])
    page = int(params[3])
    await callback.message.edit_text(
        'Выберите подкатегорию:',
        reply_markup=await kb.get_subcategories_keyboard(
            category_id=category_id,
            page=page,
        )
    )

@router.callback_query(F.data.startswith('subcategory_'))
async def get_products(callback: CallbackQuery):
    params = callback.data.split('_')
    subcategory_id = int(params[1])
    page = int(params[3])

    await callback.message.answer(
        'Выберите товар:',
        reply_markup=await kb.get_products_keyboard(
            subcategory_id=subcategory_id,
            page=page,
        )
    )
    await callback.message.delete()


@router.callback_query(F.data.startswith('product_select_'))
async def get_product(callback: CallbackQuery):
    params = callback.data.split('_')
    product_id = int(params[2])
    product = await Product.objects.filter(id=product_id).select_related('sub_category__category').afirst()
    caption = (
        f'<b>{product.name}</b>\n\n'
        f'{product.description}\n\n'
        f'Цена: {to_rub(product.price)} р.'
    )
    if product.photo:
        await callback.message.answer_photo(
            photo=FSInputFile(product.photo.path),
            caption=caption,
            reply_markup=await kb.get_product_keyboard(product)
        )
    else:
        await callback.message.answer(
            text=caption,
            reply_markup=await kb.get_product_keyboard(product)
        )
    await callback.message.delete()


@router.callback_query(F.data.startswith('add_to_cart_'))
async def add_to_cart(callback: CallbackQuery):
    params = callback.data.split('_')
    product_id = int(params[3])
    product = await Product.objects.select_related('sub_category').filter(id=product_id).afirst()

    if len(params) == 5:
        quantity = int(params[4])
        user = await TGUser.objects.filter(user_id=callback.from_user.id).select_related('cart').afirst()
        cart_item = await CartItem.objects.filter(product=product, cart__tg_user=user).afirst()
        if cart_item:
            cart_item.quantity += quantity
            await cart_item.asave()
        else:
            await CartItem.objects.acreate(
                product=product,
                cart=user.cart,
                quantity=quantity
            )

        reply_markup = await kb.get_product_keyboard(product)
        if product.photo:
            await callback.message.edit_caption(
                caption=callback.message.caption + f'\n\nДобавлено: {quantity}',
                reply_markup=reply_markup
            )
        else:
            await callback.message.edit_text(
                text=callback.message.text + f'\n\nДобавлено: {quantity}',
                reply_markup=reply_markup
            )
    else:
        await callback.message.edit_reply_markup(
            reply_markup=await kb.get_quantity_keyboard(product)
        )


@router.callback_query(F.data.startswith('remove_cart_item_'))
async def remove_cart_item(callback: CallbackQuery):
    params = callback.data.split('_')
    cart_item_id = int(callback.data.split('_')[3])
    cart_item = await CartItem.objects.filter(id=cart_item_id).afirst()
    if len(params) == 5:
        quantity = int(params[4])
        cart_item.quantity -= quantity
        if cart_item.quantity <= 0:
            await cart_item.adelete()
        else:
            await cart_item.asave()
        await get_cart(callback)
    else:
        await callback.message.edit_reply_markup(
            reply_markup=await kb.remove_cart_item_quantity(cart_item)
        )


@router.callback_query(F.data.startswith('add_order'))
async def add_order(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите адрес доставки:')
    await state.set_state(OrderStates.waiting_for_delivery_address)
    await callback.message.delete()


@router.message(OrderStates.waiting_for_delivery_address)
async def get_delivery_address(message: Message, state: FSMContext):
    delivery_address = message.text.strip()
    await state.update_data(delivery_address=delivery_address)
    await message.answer(f'Адресс доставки сохранен: {delivery_address}')
    await message.answer('Введите номер телефона:')
    await state.set_state(OrderStates.waiting_for_phone_number)

@router.message(OrderStates.waiting_for_phone_number)
async def get_phone_number(message: Message, state: FSMContext):
    phone_number = message.text.strip()
    await state.update_data(phone_number=phone_number)
    await message.answer(f'Номер телефона сохранен: {phone_number}')
    await message.answer('Создание заказа...')
    data = await state.get_data()
    user = await TGUser.objects.filter(user_id=message.from_user.id).select_related('cart').afirst()
    cart = await Cart.objects.filter(tg_user=user).prefetch_related('items__product').afirst()
    order = await Order.objects.acreate(
        delivery_address=data['delivery_address'],
        phone_number=data['phone_number'],
        tg_user=user,
    )
    total_price = 0
    message_answer = 'Заказ создан\n'
    for item in cart.items.all():
        await OrderItem.objects.acreate(
            order=order,
            product=item.product,
            quantity=item.quantity,
            product_price=item.product.price
        )
        price = item.product.price * item.quantity
        message_answer = message_answer + (
            f'=====   <b>{item.product.name}</b>   =====\n\n'
            f'{item.product.description}\n\n'
            f'Цена: {to_rub(item.product.price)}р.\n'
            f'Количесвто: {item.quantity}\n'
            f'Итого: {to_rub(price)}р.\n\n\n'
        )
        total_price += price
    message_answer = message_answer + (
        '<b>Общая сумма: ' + to_rub(await cart.total_price()) + 'р.</b>'
    )
    await cart.items.all().adelete()
    await message.answer(
        message_answer,
        reply_markup=await kb.get_paid_keyboard(order)
    )
    await message.delete()


@router.callback_query(F.data.startswith('paid_'))
async def paid(callback: CallbackQuery):
    order_id = int(callback.data.split('_')[1])
    order = await Order.objects.filter(id=order_id).afirst()

    await callback.message.answer(
        'Заказ оплачен(тут прикрутить платежку)',
        reply_markup=await kb.get_pay_keyboard(order)
    )
    await callback.message.delete()


@router.callback_query(F.data.startswith('get_order_'))
async def get_order(callback: CallbackQuery):
    order_id = int(callback.data.split('_')[2])
    order = await Order.objects.filter(id=order_id).prefetch_related('items__product').afirst()
    message_answer = f'Заказ № {order_id} от {order.created_at.strftime("%d.%m.%Y %H:%M")}\n\n'
    total_price = 0
    for item in order.items.all():
        price = item.product_price * item.quantity
        message_answer = message_answer + (
            f'=====   <b>{item.product.name}</b>   =====\n\n'
            f'{item.product.description}\n\n'
            f'Цены: {to_rub(item.product_price)}р.\n'
            f'Количество: {item.quantity}\n'
            f'Итого: {to_rub(price)}р.\n\n\n'
        )
        total_price += price
    message_answer = message_answer + (
        '<b>Общая сумма: ' + to_rub(total_price) + 'р.</b>\n\n\n'
    )
    message_answer = message_answer + (
        f'Адрес доставки: {order.delivery_address}\n'
        f'Номер телефона: {order.phone_number}\n\n'
    )
    is_paid = 'Оплачен' if order.is_paid else 'Не оплачен'
    message_answer = message_answer + (
        '<b>Статус: ' + is_paid + '</b>'
    )
    await callback.message.answer(
        message_answer,
        reply_markup=await kb.get_paid_keyboard(order, True)
    )
    await callback.message.delete()


@router.callback_query(F.data.startswith('pay_sbp'))
async def pay_sbp(callback: CallbackQuery):
    order_id = int(callback.data.split('_')[2])
    order = await Order.objects.filter(id=order_id).afirst()
    order.is_paid = True
    await order.asave()
    await callback.message.answer(
        'Заказ оплачен',
        reply_markup=await kb.get_pay_keyboard(order)
    )
    await callback.message.delete()


@router.callback_query(F.data.startswith('delete_order_'))
async def delete_order(callback: CallbackQuery):
    order_id = int(callback.data.split('_')[2])
    order = await Order.objects.filter(id=order_id).afirst()
    await order.adelete()
    await get_orders_callback(callback)
