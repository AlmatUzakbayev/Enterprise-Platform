import httpx
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))

from core.config import BACKEND_URL
from bot.keyboards import back_to_doc

router = Router()

class ChatState(StatesGroup):
    waiting_for_question = State()

@router.callback_query(F.data.startswith("ask:"))
async def start_chat(callback: CallbackQuery, state: FSMContext):
    doc_id = int(callback.data.split(":")[1])
    await state.update_data(document_id=doc_id)
    await state.set_state(ChatState.waiting_for_question)
    await callback.message.answer("❓ Введите ваш вопрос по документу:")
    await callback.answer()

@router.message(ChatState.waiting_for_question)
async def handle_question(message: Message, state: FSMContext):
    data = await state.get_data()
    doc_id = data.get("document_id")
    question = message.text

    await message.answer("🔍 Ищу ответ...")

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{BACKEND_URL}/api/v1/chat/",
            json={
                "question": question,
                "document_id": doc_id,
                "telegram_user_id": message.from_user.id,
            },
        )

    if resp.status_code == 200:
        result = resp.json()
        sources = "\n".join(result.get("sources", []))
        await message.answer(
            f"💬 {result['answer']}\n\n"
            f"📚 Источники:\n{sources}",
            reply_markup=back_to_doc(doc_id)
        )
    else:
        await message.answer("❌ Ошибка при получении ответа. Попробуйте снова.")
        await state.clear()
