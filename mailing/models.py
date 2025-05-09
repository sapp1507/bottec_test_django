from django.contrib.postgres.fields import ArrayField
from django.db import models

from utils.models import NameModel, TimeModel


class MailingCampaign(TimeModel, NameModel):
    """
    Модель представляет собой рассылку, которую можно настроить и отправить целевой группе пользователей.

    Атрибуты:
        campaign_type (str): Тип рассылки (текстовая, фото+текст, опрос).
        message_text (str): Текст сообщения рассылки.
        photo (ImageField): Фото, прикрепленное к рассылке.
        poll_question (str): Вопрос опроса (если тип рассылки — опрос).
        poll_options (ArrayField): Варианты ответов для опроса.
        target_groups (ManyToManyField): Целевая группа пользователей для рассылки.
        is_active (bool): Статус активности рассылки.
        schedule_time (DateTimeField): Время, когда запланирована отправка рассылки.
    """

    CAMPAIGN_TYPES = (
        ('text', 'Текстовая рассылка'),
        ('photo', 'Фото + текст'),
        ('poll', 'Опрос')
    )

    campaign_type = models.CharField(max_length=10, choices=CAMPAIGN_TYPES, verbose_name='Тип рассылки')
    message_text = models.TextField(verbose_name='Текст сообщения', blank=True)
    photo = models.ImageField(upload_to='mailing_photos/', verbose_name='Фото', blank=True, null=True)
    poll_question = models.CharField(max_length=100, verbose_name='Вопрос опроса', blank=True, null=True)
    poll_options = ArrayField(
        models.CharField(max_length=100),
        verbose_name='Варианты ответов',
        blank=True,
        default=list
    )
    target_groups = models.ManyToManyField('orders.TGUser', verbose_name='Целевая группа', blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    schedule_time = models.DateTimeField(verbose_name='Время отправки', null=True, blank=True)

    def __str__(self):
        return f'{self.name} ({self.get_campaign_type_display()})'

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        db_table = 'mailing_campaign'


class MailingLog(TimeModel):
    """
    Модель представляет собой журнал рассылок, который отслеживает информацию о доставке сообщений пользователям.

    Атрибуты:
        campaign (ForeignKey): Ссылка на рассылку.
        user (ForeignKey): Пользователь, которому было отправлено сообщение.
        is_sent (bool): Указывает, было ли сообщение успешно отправлено.
        error_message (str): Сообщение об ошибке, если доставка не удалась.
    """

    campaign = models.ForeignKey(
        MailingCampaign,
        on_delete=models.CASCADE,
        verbose_name='Рассылка',
        related_name='logs'
    )
    user = models.ForeignKey(
        'orders.TGUser',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='mailing_logs'
    )
    is_sent = models.BooleanField(default=False, verbose_name='Отправлено')
    error_message = models.TextField(verbose_name='Сообщение об ошибке', blank=True, null=True)

    def __str__(self):
        return f'{self.campaign.name} - {self.user.username}'

    class Meta:
        verbose_name = 'Лог рассылки'
        verbose_name_plural = 'Логи рассылок'
        db_table = 'mailing_log'
        indexes = [
            models.Index(fields=['campaign', 'user'])
        ]
