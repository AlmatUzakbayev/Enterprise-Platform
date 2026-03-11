from core.constants import RERANKER_MODEL, TOP_K_RERANK
from sentence_transformers import CrossEncoder

class RerankerService:
    def __init__(self):
        self.model = CrossEncoder(RERANKER_MODEL)

    def rerank(self, query: str, candidates: list[dict]) -> list[dict]:
        pairs = [(query, c["text"]) for c in candidates]
        scores = self.model.predict(pairs)
        for i,candidate in enumerate(candidates):
            candidate["rerank_score"] = float(scores[i])
        return sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)[:TOP_K_RERANK]