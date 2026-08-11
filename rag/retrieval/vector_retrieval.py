from database.models.closed_issue import ClosedIssue

def similarity_retrieval(db, query_vec, k: int = 20):
    distance = ClosedIssue.embeddings.cosine_distance(query_vec)
    
    rows = (
        db.query(ClosedIssue, distance.label("distance"))
        .order_by(distance)
        .limit(k)
        .all()
    )
    
    return [
        {
            "github_number":issue.github_number,
            "title": issue.title,
            "original_question": issue.original_question,
            "fix_summary": issue.fix_summary,
            "url": issue.url,
            "tags": issue.tags,
            "distance": dist,
         }
        for issue, dist in rows
    ]
    
    