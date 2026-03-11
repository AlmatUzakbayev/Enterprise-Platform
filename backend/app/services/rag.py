from langchain_core.messages import SystemMessage, HumanMessage
from langsmith import traceable

from core.constants import SYSTEM_PROMPT
from services.llm import get_llm


class RAGService:
    def __init__(self, embedder, reranker, vector_store):
        self.embedder = embedder
        self.reranker = reranker
        self.vector_store = vector_store
        self.llm = get_llm(temperature=0.1)

    @traceable(name = "rag_pipeline")
    async def answer(self, query: str, document_id: int,chat_history: list = None) -> dict:
        query_vector = self.embedder.embed_query(query)
        candidates = await self.vector_store.search(query_vector, document_id)
        reranked = self.reranker.rerank(query, candidates)

        context = "\n\n".join([f"Passage {i+1} (score: {c['rerank_score']:.4f}):\n{c['text']}" for i, c in enumerate(reranked)])
        message = [
            SystemMessage(content = SYSTEM_PROMPT),
            HumanMessage(content = f"Context:\n{context}\n\nQuestion: {query}")
        ]
        response = await self.llm.ainvoke(message)
        usage = response.response_metadata.get("token_usage") or response.response_metadata.get("usage_metadata") or {}
        tokens_used = (
            usage.get("total_tokens")
            or usage.get("total_token_count")
            or (usage.get("input_tokens", 0) + usage.get("output_tokens", 0))
            or 0
        )
        return {
            "answer": response.content,
            "sources": [
                f"Страница {c['metadata']['page_num']} (score: {round(c['rerank_score'], 4)})"
                for c in reranked
            ],
            "tokens_used": tokens_used,
            "retrieval_score": reranked[0]["rerank_score"] if reranked else 0.0,
        }
        
        
