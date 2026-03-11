from core.constants import EMBEDDINGS_MODEL
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDINGS_MODEL)
        self.dimension = self.model.get_sentence_embedding_dimension()

    def embed_query(self, query: str) -> list[float]:
        return self.model.encode(query).tolist()

    def embed_documents(self, documents: list[str]) -> list[list[float]]:
        return self.model.encode(documents).tolist()
