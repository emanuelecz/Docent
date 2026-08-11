from langchain_core.messages import ToolMessage
from langchain_core.tools import tool

from database.db import SessionLocal
from rag.embeddings.voyage_client import get_embedding_client
from rag.embeddings.embed_issue import embed_issue_text
from rag.retrieval.vector_retrieval import similarity_retrieval
from rag.retrieval.keyword_retriever import keyword_retrieval
from rag.retrieval.merge import merge
from rag.retrieval.reranker import rerank
from agent.state import AgentState
from agent.research.github_mcp import get_github_tools



@tool
def search_corpus(query: str) -> list[dict]:
    """Search Docent's corpus of already-RESOLVED issues in this repo. Returns the most
    similar past issues, each with its original problem and how it was fixed. Use one
    focused query describing the core problem in your own words."""
    client = get_embedding_client()
    qvec = embed_issue_text(client, query, input_type="query")

    db = SessionLocal()
    try:
        sim = similarity_retrieval(db, qvec, k=20)
        kw = keyword_retrieval(db, query, k=20)
    finally:
        db.close()

    merged = merge(sim, kw)
    return rerank(merged[:30], query, top_k=6)


def _format_hits(hits: list[dict]) -> str:
    if not hits:
        return "No similar resolved issues found in the corpus."
    lines = []
    for h in hits:
        lines.append(
            f"- #{h['github_number']} {h['title']} ({h['url']})\n"
            f"  problem: {h['original_question'][:300]}\n"
            f"  fix: {h['fix_summary'][:300]}"
        )
    return "Similar resolved issues:\n" + "\n".join(lines)
    
async def tools_node(state: AgentState) -> dict:
    last = state["messages"][-1]
    github_tools = await get_github_tools()
    by_name = {t.name: t for t in github_tools}
    tool_messages: list[ToolMessage] = []
    log: list[dict] = []
    updates: dict = {}
    corpus_done = state.get("rag_used", False)
    
    for call in last.tool_calls:
        name, args, call_id = call["name"], call["args"], call["id"]
        
        if name == "search_corpus":
            if corpus_done:
                content = "Corpus already searched once - reuse the earlier results"
            else:
                hits = await search_corpus.ainvoke(args)
                updates["retrieved"] = hits
                updates["rag_used"] = True
                corpus_done = True
                content = _format_hits(hits)
        else:
            gh_tool = by_name.get(name)
            if gh_tool is None:
                content = f"Unknown tool: {name}"
            else: 
                result = await gh_tool.ainvoke(args)
                content = result if isinstance(result,str) else str(result)
                
        tool_messages.append(ToolMessage(content=content,tool_call_id=call_id))
        log.append({"name":name, "args":args})
        
    updates["messages"] = tool_messages
    updates["tool_calls"] = log
    return updates