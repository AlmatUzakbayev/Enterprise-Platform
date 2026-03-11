from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue,
    PayloadSchemaType,
)
from core.config import QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION
import uuid

class VectorStore:
    def __init__(self):
        self.client = AsyncQdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
        )
        self.collection = QDRANT_COLLECTION

    async def ensure_collection(self, vector_size: int):
        collections = await self.client.get_collections()
        names = [c.name for c in collections.collections]

        if self.collection not in names:
            await self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                ),
            )

        await self.client.create_payload_index(
            collection_name=self.collection,
            field_name="document_id",
            field_schema=PayloadSchemaType.INTEGER,
        )

    async def upsert_chunks(self, document_id: int, chunks: list[dict], embeddings: list[list[float]]):
        points = []
        for chunk, vector in zip(chunks, embeddings):
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "document_id": document_id,
                    "text": chunk["text"],
                    "chunk_index": chunk["chunk_index"],
                    "page_num": chunk["page_num"],
                    "char_start": chunk["char_start"],
                },
            ))

        await self.client.upsert(
            collection_name=self.collection,
            points=points,
        )

    async def search(self, query_vector: list[float], document_id: int, top_k: int = 10) -> list[dict]:
        results = await self.client.query_points(
            collection_name=self.collection,
            query=query_vector,
            query_filter=Filter(
                must=[FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id),
                )]
            ),
            limit=top_k,
            with_payload=True,
        )

        return [
            {
                "text": r.payload["text"],
                "score": r.score,
                "metadata": {
                    "document_id": r.payload["document_id"],
                    "chunk_index": r.payload["chunk_index"],
                    "page_num": r.payload["page_num"],
                },
            }
            for r in results.points
        ]

    async def delete_document(self, document_id: int):
        await self.client.delete(
            collection_name=self.collection,
            points_selector=Filter(
                must=[FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id),
                )]
            ),
        )
