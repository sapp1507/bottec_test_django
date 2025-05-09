import asyncio

from aiogram import Dispatcher

from bot.handlers.user import router
from bot.loader import bot, dp
from bot.middlewares import middleware_list
from core.settings import logging_bot as log




async def _on_shutdown(dispatcher: Dispatcher):
    """Выполняется при остановке бота."""
    await bot.close()
    await dispatcher.storage.close()
    log.info('Bot stopped!')


def run_bot():
    """Запускает бота."""
    log.info('Bot started!')

    dp.include_router(router)

    for middleware in middleware_list:
        dp.message.outer_middleware(middleware)
        dp.callback_query.outer_middleware(middleware)
        dp.chat_join_request.outer_middleware(middleware)

    try:
        asyncio.run(dp.start_polling(
            bot,
            on_shutdown=_on_shutdown)
        )
    except KeyboardInterrupt:
        log.info('Bot interrupted by user.')
    except Exception as e:
        log.error(f'Bot error: {e}')
    finally:
        log.info('Bot shutdown process completed.')
