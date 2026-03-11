import httpx
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))

from core.config import BACKEND_URL
from bot.keyboards import document_menu, main_menu

router = Router()


@router.callback_query(F.data == "upload_doc")
async def ask_upload(callback: CallbackQuery):
    await callback.message.answer("📎 Отправьте файл (PDF, DOCX или TXT) в этот чат:")
    await callback.answer()


@router.callback_query(F.data == "list_docs")
async def list_docs(callback: CallbackQuery):
    user_id = callback.from_user.id
    print(f"[bot] list_docs pressed by user_id={user_id}")
    await callback.answer()
    async with httpx.AsyncClient(timeout=30) as client:
        # Запрашиваем как документы текущего пользователя, так и незаданные (telegram_user_id=0)
        # Используем Supabase REST-style filter через query params: or=(telegram_user_id.eq.<id>,telegram_user_id.eq.0)
        params = {
            "or": f"telegram_user_id.eq.{user_id},telegram_user_id.eq.0",
            "select": "*",
        }
        resp = await client.get(
            f"{BACKEND_URL}/api/v1/documents/",
            params=params,
        )

    print(f"[bot] list_docs: backend status={resp.status_code}")
    try:
        body = resp.json()
    except Exception as e:
        print(f"[bot] list_docs: failed to parse json: {e}")
        await callback.message.answer("Ошибка связи с бэкендом. Попробуйте позже.")
        return

    print(f"[bot] list_docs: backend returned {len(body) if isinstance(body, list) else 'non-list'} items")

    count = len(body) if isinstance(body, list) else 0
    await callback.message.answer(f"🔎 Найдено документов: {count}")

    if resp.status_code != 200 or not body:
        await callback.message.answer("📂 У вас пока нет загруженных документов.")
        return

    docs = body
    for doc in docs:
        summary = doc.get("summary") or "Нет описания"
        await callback.message.answer(
            f"📄 *{doc['filename']}*\n📝 {summary[:200]}...",
            parse_mode="Markdown",
            reply_markup=document_menu(doc['id'])
        )


@router.callback_query(F.data == "main_menu")
async def go_main_menu(callback: CallbackQuery):
    await callback.message.answer("Главное меню:", reply_markup=main_menu())
    await callback.answer()


@router.callback_query(F.data.startswith("doc_menu:"))
async def doc_menu_callback(callback: CallbackQuery):
    doc_id = int(callback.data.split(":")[1])
    await callback.message.answer("Меню документа:", reply_markup=document_menu(doc_id))
    await callback.answer()


@router.callback_query(F.data.startswith("delete:"))
async def delete_doc(callback: CallbackQuery):
    doc_id = int(callback.data.split(":")[1])
    await callback.answer()
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.delete(
            f"{BACKEND_URL}/api/v1/documents/{doc_id}",
            params={"telegram_user_id": callback.from_user.id},
        )
    if resp.status_code == 200:
        await callback.message.answer("🗑 Документ удалён.", reply_markup=main_menu())
    else:
        await callback.message.answer("❌ Ошибка при удалении документа.")


@router.message(F.document)
async def handle_file(message: Message):
    doc = message.document
    filename = doc.file_name

    file = await message.bot.get_file(doc.file_id)
    file_bytes = await message.bot.download_file(file.file_path)

    await message.answer("⏳ Загружаю документ, подождите...")

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{BACKEND_URL}/api/v1/documents/upload",
            files={"file": (filename, file_bytes)},
            data={"telegram_user_id": message.from_user.id},
        )

    print(f"[bot] upload document response: status={resp.status_code}")
    try:
        result = resp.json()
    except Exception as e:
        print(f"[bot] upload parse json error: {e}")
        await message.answer("❌ Ошибка при загрузке документа. Попробуйте снова.")
        return

    if resp.status_code == 200:
        summary = result.get("summary") or "Краткое содержание недоступно"
        await message.answer(
            f"✅ Документ загружен!\n\n"
            f"📄 *{result['filename']}*\n\n"
            f"📝 {summary}",
            parse_mode="Markdown",
            reply_markup=document_menu(result['id'])
        )
    else:
        await message.answer("❌ Ошибка при загрузке документа. Попробуйте снова.")
