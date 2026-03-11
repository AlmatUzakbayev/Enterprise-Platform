from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="My Documents", callback_data="list_docs"),
        InlineKeyboardButton(text="Upload Document", callback_data="upload_doc"),
    )

    return builder.as_markup()

def document_menu(document_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Ask a Question", callback_data=f"ask:{document_id}"),
        InlineKeyboardButton(text="Summarize Document", callback_data=f"summarize:{document_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="Back to Main Menu", callback_data="main_menu"),
        InlineKeyboardButton(text="Delete Document", callback_data=f"delete:{document_id}"),
    )

    return builder.as_markup()

def back_to_doc(document_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Ask Another Question", callback_data=f"ask:{document_id}"),
        InlineKeyboardButton(text="Back to Document Menu", callback_data=f"doc_menu:{document_id}"),
    )

    return builder.as_markup()
