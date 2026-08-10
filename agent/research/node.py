from database.db import SessionLocal
from agent.state import AgentState
from rag.retrieval.vector_retrieval import similarity_retrieval
from rag.retrieval.keyword_retriever import keyword_retrieval
from rag.retrieval.merge import merge
from rag.retrieval.reranker import rerank


def research(state: AgentState) -> dict:
    query_vec = state["embedding"]
    keyword_query = state["title"]
    rerank_query = state["body_summary"] or state["original_question"]

    db = SessionLocal()
    try:
        similarity_hits = similarity_retrieval(db, query_vec, k=20)
        keyword_hits = keyword_retrieval(db, keyword_query, k=20)
    finally:
        db.close()

    merged = merge(similarity_hits, keyword_hits)
    reranked = rerank(merged[:30], rerank_query, top_k=6)

    return {"retrieved": reranked}
