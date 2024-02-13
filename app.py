from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommandScopeAllPrivateChats
from database.engine import create_db, drop_db, session_maker
from handlers.admin_private import admin_router
from handlers.user_group import user_group_router
from handlers.user_private import user_private_router
from common.bot_commands_list import private
from middlewares.db import DataBaseSession

# ALLOWED_UPDATES = ['message', 'edited_message', 'callback_query']
bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
bot.my_admins_list = []

dp = Dispatcher()
dp.include_routers(user_group_router, user_private_router, admin_router)


async def on_startup():
    run_program = False
    if run_program:
        await drop_db()

    await create_db()


async def on_shutdown():
    print('Бот впав')


async def main():
    # await create_db()
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)
    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=private, scope=BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


asyncio.run(main())
