from fastapi import APIRouter, HTTPException, Request
from supabase import Client

from database.database import get_db
from services.vector_store import VectorStore
from services.rag import RAGService
from data import ChatRequest, ChatResponse, MessageResponse
from core.constants import MAX_HISTORY_MESSAGES

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    request: Request,
):
    db: Client = get_db()

    result = db.table("documents").select("*").eq("id", payload.document_id).execute()
    if not result.data:
        raise HTTPException(404, "Документ не найден")

    history_result = (
        db.table("chat_messages")
        .select("*")
        .eq("telegram_user_id", payload.telegram_user_id)
        .eq("document_id", payload.document_id)
        .order("created_at", desc=True)
        .limit(MAX_HISTORY_MESSAGES)
        .execute()
    )
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in reversed(history_result.data)
    ]

    vs = VectorStore()
    rag = RAGService(
        embedder=request.app.state.embedder,
        reranker=request.app.state.reranker,
        vector_store=vs,
    )

    answer_result = await rag.answer(
        query=payload.question,
        document_id=payload.document_id,
        chat_history=history,
    )

    db.table("chat_messages").insert({
        "telegram_user_id": payload.telegram_user_id,
        "document_id": payload.document_id,
        "role": "user",
        "content": payload.question,
    }).execute()

    db.table("chat_messages").insert({
        "telegram_user_id": payload.telegram_user_id,
        "document_id": payload.document_id,
        "role": "assistant",
        "content": answer_result["answer"],
        "tokens_used": answer_result["tokens_used"],
        "retrieval_score": answer_result["retrieval_score"],
    }).execute()

    return ChatResponse(**answer_result)


@router.get("/history", response_model=list[MessageResponse])
async def get_history(
    telegram_user_id: int,
    document_id: int,
    limit: int = 20,
):
    db: Client = get_db()
    result = (
        db.table("chat_messages")
        .select("*")
        .eq("telegram_user_id", telegram_user_id)
        .eq("document_id", document_id)
        .order("created_at", desc=False)
        .limit(limit)
        .execute()
    )
    return result.data
