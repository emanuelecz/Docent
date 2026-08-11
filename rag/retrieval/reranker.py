from core.config import get_settings
from rag.embeddings.voyage_client import get_embedding_client

settings = get_settings()


def rerank(candidates, query_text, top_k: int = 10):
    if not candidates:
        return []

    client = get_embedding_client()
    documents = [f"{c['title']}\n{c['original_question']}" for c in candidates]

    result = client.rerank(
        query_text,
        documents,
        model=settings.rerank_model,
        top_k=top_k,
    )

    return [
        {**candidates[r.index], "rerank_score": r.relevance_score}
        for r in result.results
    ]
