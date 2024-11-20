import asyncio
from os import supports_fd

from aiogram.types import Message
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from app.handlers import router
from app.database.models import async_main

supports_canal = '-1002335317649'

async def main():
    await async_main()
    bot = Bot(token='7882619849:AAF4WABwNdKvnQ39-mgh0STAztWMyD-VXpM')
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот спит')

