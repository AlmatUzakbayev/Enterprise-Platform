import os
import aiofiles
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from supabase import Client

from database.database import get_db
from services.parser import parse_document
from services.chunker import chunk_text
from services.vector_store import VectorStore
from services.summarizer import summarize_document
from data import DocumentResponse
from core.constants import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_BYTES, UPLOAD_DIR

router = APIRouter()
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    telegram_user_id: int = Form(0),
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Поддерживаются только: {ALLOWED_EXTENSIONS}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(400, "Файл слишком большой (макс. 20MB)")

    file_path = os.path.join(UPLOAD_DIR, f"{telegram_user_id}_{file.filename}")
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    parsed = parse_document(file_path)
    chunks = chunk_text(parsed["text"], parsed["page_map"]) if parsed.get("text") else []

    embedder = request.app.state.embedder
    embeddings = embedder.embed_documents([c["text"] for c in chunks]) if chunks else []

    vs = VectorStore()
    await vs.ensure_collection(embedder.dimension)

    db: Client = get_db()

    result = db.table("documents").insert({
        "filename": file.filename,
        "file_type": parsed.get("file_type","unknown"),
        "language": parsed.get("language","unknown"),
        "chunk_count": len(chunks),
        "telegram_user_id": telegram_user_id,
    }).execute()

    doc = result.data[0]
    doc_id = doc["id"]

    if chunks and embeddings:
        await vs.upsert_chunks(doc_id, chunks, embeddings)

    summary = await summarize_document(parsed.get("text",""), parsed.get("language","")) if parsed.get("text") else None
    if summary:
        db.table("documents").update({"summary": summary}).eq("id", doc_id).execute()
        doc["summary"] = summary

    return doc


@router.get("/", response_model=list[DocumentResponse])
async def list_documents(request: Request, telegram_user_id: int | None = None):
    db: Client = get_db()

    # If explicit telegram_user_id provided, use it
    if telegram_user_id is not None:
        result = (
            db.table("documents")
            .select("*")
            .eq("telegram_user_id", telegram_user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data

    # Support Supabase-style OR filter sent by bot: or=telegram_user_id.eq.<id>,telegram_user_id.eq.0
    or_param = request.query_params.get("or")
    if or_param:
        # try extract non-zero user id
        parts = or_param.split(",")
        user_id = None
        for p in parts:
            if p.startswith("telegram_user_id.eq."):
                val = p.split(".")[-1]
                if val != "0":
                    try:
                        user_id = int(val)
                        break
                    except Exception:
                        pass
        if user_id is not None:
            r1 = db.table("documents").select("*").eq("telegram_user_id", user_id).order("created_at", desc=True).execute()
            r2 = db.table("documents").select("*").eq("telegram_user_id", 0).order("created_at", desc=True).execute()
            # combine, place user docs first, then public, avoid duplicates
            ids = set()
            combined = []
            for item in r1.data + r2.data:
                if item["id"] in ids:
                    continue
                ids.add(item["id"])
                combined.append(item)
            return combined

    # fallback: return empty list
    return []


@router.delete("/{document_id}")
async def delete_document(document_id: int, telegram_user_id: int):
    db: Client = get_db()

    result = (
        db.table("documents")
        .select("*")
        .eq("id", document_id)
        .eq("telegram_user_id", telegram_user_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(404, "Документ не найден")

    vs = VectorStore()
    await vs.delete_document(document_id)

    db.table("chat_messages").delete().eq("document_id", document_id).execute()
    db.table("documents").delete().eq("id", document_id).execute()

    return {"status": "deleted", "document_id": document_id}