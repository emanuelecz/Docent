from functools import lru_cache
from langchain_mcp_adapters.client import MultiServerMCPClient
from core.config import get_settings

settings = get_settings()

ALLOWED_TOOLS = {
    "issue_read",
    "list_issues",
    "search_issues",
    "pull_request_read",
    "list_pull_requests",
    "search_pull_requests",
    "get_file_contents",
    "get_commit",
    "list_commits",
    "search_code",
}


@lru_cache
def _client() -> MultiServerMCPClient:
    return MultiServerMCPClient(
        {
            "github": {
                "transport": "streamable_http",
                "url": settings.github_mcp_url,
                "headers": {
                    "Authorization": f"Bearer {settings.github_pat_key}",
                    "X-MCP-Readonly": "true",
                    "X-MCP-Toolsets": "all",
                }
            }
        }
    )
    
    
_cached_tools: list | None = None

async def get_github_tools() -> list:
    """Load Github MCP tools once, filtered to a read-only allow-list."""
    global _cached_tools
    if _cached_tools is None:
        all_tools = await _client().get_tools()
        _cached_tools = [t for t in all_tools if t.name in ALLOWED_TOOLS]
    return _cached_tools