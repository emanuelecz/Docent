from sqlalchemy import func
from database.models.closed_issue import ClosedIssue

def keyword_retrieval(db, query_text, k:int = 20):
    query = func.websearch_to_tsquery("english", query_text)
    rank = func.ts_rank_cd(ClosedIssue.search_vector, query, 32)
    
    rows = (
        db.query(ClosedIssue, rank.label("rank"))
        .filter(ClosedIssue.search_vector.op("@@")(query))
        .order_by(rank.desc())
        .limit(k)
        .all()
    )
    
    return [
        {
            "github_number": issue.github_number,
            "title": issue.title,
            "original_question": issue.original_question,
            "fix_summary": issue.fix_summary,
            "url": issue.url,
            "tags": issue.tags,
            "rank": rnk,
        }
        for issue, rnk in rows
    ]