import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'app'))

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart

from bot.keyboards import main_menu
from core.config import TELEGRAM_BOT_TOKEN
from handler.documents import router as documents_router
from handler.chat import router as chat_router

async def main():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    @dp.message(CommandStart())
    async def cmd_start(message):
        await message.answer(
            "Добро пожаловать в EnterprisePlatform Bot!\n\n"
            "Вы можете загружать PDF, DOCX или TXT файлы и задавать вопросы по их содержимому.\n\n"
            "Загрузите документ и задайте вопрос — я отвечу на основе содержимого!",
            reply_markup=main_menu()
        )

    dp.include_router(documents_router)
    dp.include_router(chat_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())