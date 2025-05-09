from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.enums import ChatMemberStatus
from aiogram.types import TelegramObject, User
from django.utils.html import avoid_wrapping

from bot.loader import GROUP_CHAT_ID, bot
from orders.models import TGUser, Cart

last_messages_ids = {}



class UserMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data:Dict[str, Any]
                       ):
        tg_user: Optional[User] = self._extract_user(event)
        if tg_user:
            user = await self._update_or_create_user(tg_user)
            await Cart.objects.aget_or_create(tg_user=user)
            user_channel_status = await bot.get_chat_member(
                chat_id=GROUP_CHAT_ID,
                user_id=tg_user.id
            )
            if user_channel_status.status == ChatMemberStatus.LEFT:
                user.is_subscribe = False
                await bot.send_message(
                    chat_id=tg_user.id,
                    text=avoid_wrapping(
                        'Добро пожаловать в бота! '
                        'Для работы с ботом необходимо присоединиться к каналу https://t.me/bottecnotec_test'
                    )
                )
                await event.delete()
                return
            else:
                user.is_subscribe = True
                await user.asave()

        return await handler(event, data)

    @staticmethod
    def _extract_user(event: TelegramObject) -> Optional[User]:
        if hasattr(event, 'from_user') and event.from_user:
            return event.from_user

        if hasattr(event, 'message') and event.message:
            return event.message.from_user

        return None

    @staticmethod
    async def _update_or_create_user(tg_user: User):
        obj, _ = await TGUser.objects.aget_or_create(
            user_id=tg_user.id,
            defaults={
                'username': tg_user.username or '',
                'full_name': tg_user.full_name,
            }
        )

        changed = False

        new_username = tg_user.username or ''
        new_fullname = tg_user.full_name

        if obj.username != new_username:
            obj.username = new_username
            changed = True

        if obj.full_name != new_fullname:
            obj.full_name = new_fullname
            changed = True

        if changed:
            await obj.asave()

        return obj
