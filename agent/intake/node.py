from database.models.open_issue import OpenIssue
from database.db import SessionLocal
from rag.embeddings.embed_issue import issue_embed_text, embed_issue_text
from agent.state import AgentState
from ai.summary_llm import summarize_original_question
from rag.embeddings.voyage_client import get_embedding_client

def intake(state: AgentState) -> dict:
    number = state["github_number"]

    db = SessionLocal()
    try:
        open_issue = db.query(OpenIssue).filter(OpenIssue.github_number == number).first()
        if open_issue.body_summary is not None and open_issue.embeddings is not None:
            summary, vec = open_issue.body_summary, open_issue.embeddings
        else:
            title = open_issue.title
            original_question = open_issue.original_question
            summary = summarize_original_question(title=title, original_question=original_question)
            text_to_embed = issue_embed_text(title, original_question)
            emb_client = get_embedding_client()
            vec = embed_issue_text(emb_client, text_to_embed, input_type="query")
            open_issue.body_summary = summary
            open_issue.embeddings = vec
            db.commit()
        return {"body_summary": summary, "embedding": vec}
    finally:
        db.close()
