from django.db import models

from utils.models import NameModel, TimeModel


class FAQCategory(TimeModel, NameModel):
    """
    Модель категории Вопрос-ответ.

    Описывает категорию, к которой могут относиться элементы FAQ (вопросы и ответы).

    Attributes:
        name (str): Название категории.
        priority (int): Приоритет сортировки категории (по умолчанию 0).
    """

    priority = models.IntegerField(default=0, verbose_name='Приоритет сортировки')

    class Meta:
        verbose_name = 'Категория FAQ'
        verbose_name_plural = 'Категории FAQ'
        ordering = ['priority']
        db_table = 'faq_category'


class FAQItem(TimeModel):
    """
    Модель Вопрос-ответ.

    Описывает отдельный элемент FAQ — вопрос и связанный с ним ответ.

    Attributes:
        category (FAQCategory): Категория, к которой принадлежит элемент.
        question (str): Текст вопроса.
        answer (str): Текст ответа.
        is_active (bool): Статус активности элемента (по умолчанию True).
        priority (int): Приоритет сортировки элемента (по умолчанию 0).
    """

    category = models.ForeignKey(
        FAQCategory,
        on_delete=models.CASCADE,
        verbose_name='Категория',
        related_name='faq_items',
        blank=True,
        null=True
    )
    question = models.CharField(max_length=255, verbose_name='Вопрос')
    answer = models.TextField(verbose_name='Ответ', blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    priority = models.IntegerField(default=0, verbose_name='Приоритет сортировки')

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = 'Вопрос-ответ'
        verbose_name_plural = 'Вопросы-ответы'
        ordering = ['priority']
        db_table = 'faq_item'
