from django.db import models

from utils.models import NameModel, TimeModel


class Category(TimeModel, NameModel):
    """
    Модель категории товаров.

    Описывает основные категории, к которым могут относиться подкатегории и товары.

    Attributes:
        name (str): Название категории (унаследовано от NameModel).
    """

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        db_table = 'category'


class SubCategory(TimeModel, NameModel):
    """
    Модель подкатегории товара.

    Описывает подкатегорию, принадлежащую определённой категории.

    Attributes:
        name (str): Название подкатегории (унаследовано от NameModel).
        category (Category): Ссылка на родительскую категорию.
        description (str): Описание подкатегории (необязательное поле).
    """

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория',
        related_name='sub_categories'
    )
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'
        db_table = 'sub_category'


class Product(TimeModel, NameModel):
    """
    Модель товара.

    Описывает конкретный товар, доступный в магазине.

    Attributes:
        name (str): Название товара.
        sub_category (SubCategory): Ссылка на подкатегорию, к которой относится товар.
        description (str): Описание товара (необязательное поле).
        photo (ImageField): Фотография товара (необязательное поле).
        price (int): Цена товара.
        count (int): Количество товара на складе.
        is_available (bool): Флаг, указывающий, доступен ли товар для заказа (по умолчанию True).
    """

    name = models.CharField(max_length=200)
    sub_category = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE,
        verbose_name='Категория',
        related_name='products'
    )
    description = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to='products/', null=True, blank=True)
    price = models.IntegerField()
    count = models.IntegerField()
    is_available = models.BooleanField(default=True, verbose_name='Доступен')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        db_table = 'product'

