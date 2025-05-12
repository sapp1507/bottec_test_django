from django.db import models
from django.contrib.postgres.fields import ArrayField
from orders.models import TGUser
from utils.models import TimeModel


class MailingCampaign(TimeModel):
    class CampaignType(models.TextChoices):
        TEXT = 'text', 'Текстовая рассылка'
        PHOTO = 'photo', 'Фото + текст'
        POLL = 'poll', 'Опрос'

    name = models.CharField('Название', max_length=100)
    campaign_type = models.CharField('Тип', max_length=10, choices=CampaignType.choices)
    message_text = models.TextField('Текст сообщения', blank=True)
    photo = models.ImageField('Фото', upload_to='mailings/', blank=True, null=True)
    poll_question = models.CharField('Вопрос', max_length=255, blank=True)
    poll_options = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    target_groups = models.ManyToManyField(TGUser, verbose_name='Целевые группы', blank=True)
    is_active = models.BooleanField('Активна', default=True)
    scheduled_time = models.DateTimeField('Время отправки', null=True, blank=True)
    is_completed = models.BooleanField('Завершена', default=False)

    def __str__(self):
        return f"{self.name} ({self.get_campaign_type_display()})"

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        indexes = [
            models.Index(fields=['is_active', 'scheduled_time'])
        ]


class MailingLog(TimeModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'В ожидании'
        SENT = 'sent', 'Отправлено'
        FAILED = 'failed', 'Ошибка'

    campaign = models.ForeignKey(MailingCampaign, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(TGUser, on_delete=models.CASCADE, related_name='mailing_logs')
    status = models.CharField(
        'Статус',
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    error_message = models.TextField('Ошибка', blank=True)
    sent_at = models.DateTimeField('Время отправки', null=True)

    class Meta:
        verbose_name = 'Лог рассылки'
        verbose_name_plural = 'Логи рассылок'
        unique_together = ('campaign', 'user')
