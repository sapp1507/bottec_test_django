from django.core.management.base import BaseCommand
from django.utils import timezone

from mailing.models import MailingCampaign, MailingLog
from asgiref.sync import sync_to_async
import asyncio
from aiogram import Bot
from django.conf import settings


class Command(BaseCommand):
    help = 'Отправка запланированных рассылок через Telegram бота'

    def handle(self, *args, **options):
        asyncio.run(self.send_mailings())

    async def send_mailings(self):
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        campaigns = await sync_to_async(list)(
            MailingCampaign.objects.filter(
                is_active=True,
                is_completed=False,
                scheduled_time__lte=timezone.now()
            ).prefetch_related('target_groups')
        )

        for campaign in campaigns:
            await self.process_campaign(bot, campaign)

    async def process_campaign(self, bot, campaign):
        users = await sync_to_async(list)(campaign.target_groups.all())

        for user in users:
            try:
                await getattr(self, f'send_{campaign.campaign_type}')(bot, user, campaign)
                await self.log_success(campaign, user)
            except Exception as e:
                await self.log_failure(campaign, user, str(e))

        campaign.is_completed = True
        await campaign.asave()

    async def send_text(self, bot, user, campaign):
        await bot.send_message(
            chat_id=user.telegram_id,
            text=campaign.message_text
        )

    async def send_photo(self, bot, user, campaign):
        with open(campaign.photo.path, 'rb') as photo:
            await bot.send_photo(
                chat_id=user.telegram_id,
                photo=photo,
                caption=campaign.message_text
            )

    async def send_poll(self, bot, user, campaign):
        await bot.send_poll(
            chat_id=user.telegram_id,
            question=campaign.poll_question,
            options=campaign.poll_options,
            is_anonymous=False
        )

    @sync_to_async
    def log_success(self, campaign, user):
        MailingLog.objects.update_or_create(
            campaign=campaign,
            user=user,
            defaults={
                'status': MailingLog.Status.SENT,
                'sent_at': timezone.now()
            }
        )

    @sync_to_async
    def log_failure(self, campaign, user, error):
        MailingLog.objects.update_or_create(
            campaign=campaign,
            user=user,
            defaults={
                'status': MailingLog.Status.FAILED,
                'error_message': error[:500]
            }
        )