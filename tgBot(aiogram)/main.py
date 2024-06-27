import os
import asyncio

from aiogram import Bot, Dispatcher
# from aiogram.types import BotCommandScopeAllPrivateChats
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties


from hendlers.user import user_router
from hendlers.admin import admin_router
# from hendlers.cmd import cmd

from middlewares.db import DataBaseSession

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from database.engine import create_tables, async_session


bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
bot.my_admins_list = [794262771]

dp = Dispatcher()

dp.include_router(user_router)
dp.include_router(admin_router)


async def on_startup(bot):
    await create_tables()


async def on_shutdown(bot):
    print('Бот лежит')


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=async_session))

    await bot.delete_webhook(drop_pending_updates=True)
    # await bot.delete_my_commands(scope=BotCommandScopeAllPrivateChats())
    # await bot.set_my_commands(commands=cmd, scope=BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    asyncio.run(main())
