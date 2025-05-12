from django.db import models

from products.models import Product
from utils.models import TimeModel


class TGUser(TimeModel):
    """
    Модель пользователя Telegram.

    Описывает пользователя, взаимодействующего с ботом.

    Attributes:
        user_id (BigIntegerField): Уникальный идентификатор пользователя в Telegram.
        username (str): Имя пользователя (может быть пустым).
        full_name (str): Полное имя пользователя (может быть пустым).
    """

    user_id = models.BigIntegerField(unique=True, verbose_name='Телеграм ID')
    username = models.CharField(max_length=100, null=True, blank=True, verbose_name='Имя пользователя')
    full_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='ФИО')

    def __str__(self):
        return f'{self.username if self.username else ""}(@{self.username})'

    class Meta:
        verbose_name = 'Пользователь Telegram'
        verbose_name_plural = 'Пользователи Telegram'
        db_table = 'tg_user'


class Cart(TimeModel):
    """
    Модель корзины пользователя.

    Содержит товары, выбранные пользователем перед оформлением заказа.

    Attributes:
        tg_user (TGUser): Пользователь Telegram, которому принадлежит корзина.
    """

    tg_user = models.OneToOneField(TGUser, on_delete=models.CASCADE, verbose_name='Пользователь')

    async def total_price(self):
        """Считает общую стоимость всех товаров в корзине."""
        total = 0
        async for item in self.items.all():
            total += item.product.price * item.quantity
        return total

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        db_table = 'cart'


class CartItem(TimeModel):
    """
    Модель элемента корзины — конкретный товар и его количество.

    Attributes:
        cart (Cart): Корзина, к которой относится товар.
        product (Product): Товар, добавленный в корзину.
        quantity (int): Количество товара (по умолчанию 1).
    """

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        verbose_name='Корзина',
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Товар',
        related_name='cart_items'
    )
    quantity = models.IntegerField(default=1, verbose_name='Количество')

    @property
    def price(self):
        """Считает стоимость товара с учетом его количества."""

        return self.product.price * self.quantity

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    class Meta:
        verbose_name = 'Товар корзины'
        verbose_name_plural = 'Товары корзины'
        db_table = 'cart_item'


class Order(TimeModel):
    """
    Модель заказа пользователя.

    Описывает оформленный пользователем заказ с контактной информацией и адресом доставки.

    Attributes:
        tg_user (TGUser): Пользователь Telegram, сделавший заказ.
        delivery_address (str): Адрес доставки.
        phone_number (str): Номер телефона для связи.
        is_paid (bool): Флаг оплаты заказа (по умолчанию False).
    """

    tg_user = models.ForeignKey(TGUser, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='orders')
    delivery_address = models.TextField(verbose_name='Адрес доставки')
    phone_number = models.CharField(max_length=20, verbose_name='Номер телефона')
    is_paid = models.BooleanField(default=False, verbose_name='Оплачено')

    def __str__(self):
        return f'Заказ #{self.id} от {self.created_at}, пользователь: {self.tg_user}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        db_table = 'order'


class OrderItem(models.Model):
    """
    Модель элемента заказа — конкретный товар и его количество в заказе.

    Attributes:
        order (Order): Заказ, к которому относится товар.
        product (Product): Товар, вошедший в заказ.
        quantity (PositiveIntegerField): Количество товара (по умолчанию 1).
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ', related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар', related_name='order_items')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    product_price = models.IntegerField(verbose_name='Цена товара в копейках')

    @property
    def price(self):
        """Считает стоимость товара с учетом его количества."""

        return self.product.price * self.quantity

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    class Meta:
        verbose_name = 'Товар заказа'
        verbose_name_plural = 'Товары заказа'
        db_table = 'order_item'
