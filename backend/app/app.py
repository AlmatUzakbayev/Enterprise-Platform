from fastapi import FastAPI
from contextlib import asynccontextmanager

from services.embeddings import EmbeddingService
from services.reranker import RerankerService

from api.documents import router as documents_router
from api.chat import router as chat_router

@asynccontextmanager
async def lifespan(app: FastAPI):

    app.state.embedder = EmbeddingService()
    app.state.reranker = RerankerService()

    yield

app = FastAPI(
    title="EnterprisePlatform API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(documents_router, prefix="/api/v1/documents")
app.include_router(chat_router, prefix="/api/v1/chat")


@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8080)