import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.handlers.user import router
from bot.loader import bot, dp
from bot.middlewares import middleware_list
from core.settings import logging_bot as log

# @dp.message(CommandStart())
# async def cmd_start(message: Message):
#     await message.answer('Hello! Shit')
#
# @dp.message(Command('help'))
# async def get_help(message: Message):
#     await message.answer('Help!')
#
# @dp.message(F.text == 'fuck')
# async def get_fuck(message: Message):
#     await message.answer('Fuck!')
#
# @dp.message(Command('get_photo'))
# async def get_photo(message: Message):
#     await message.answer_photo(photo='https://ya.ru/images/search?pos=0&from=tabbar&img_url=https%3A%2F%2Fcs6.pikabu.ru%2Fpost_img%2Fbig%2F2015%2F06%2F08%2F3%2F1433735650_472905306.jpg&text=%D0%BA%D0%B0%D1%80%D1%82%D0%B8%D0%BD%D0%BA%D0%B8&rpt=simage&lr=192',
#                                caption='Просто фото')


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
