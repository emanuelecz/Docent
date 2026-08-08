from schemas.issues_schemas import FetchedIssue
import requests
from core.config import get_settings

settings = get_settings()
REPO_OWNER = settings.repo_owner
REPO_NAME = settings.repo_name

def fetch_latest_open_issue(token:str):
  query = """
    query($q: String!) {
      search(query: $q, type: ISSUE, first: 1) {
        edges {
          node {
            ... on Issue {
              number
              title
              url
              body
              closedAt
              labels(first: 10) { nodes { name } }
            }
          }
        }
      }
    }
    """
  variables = {"q": f"repo:{REPO_OWNER}/{REPO_NAME} is:issue is:open sort:created-desc"}
  headers = {"Authorization": f"Bearer {token}"}
  response = requests.post(
      "https://api.github.com/graphql",
      json={"query": query, "variables": variables},
      headers=headers
  )
  response.raise_for_status()
  data = response.json()
  
  open_issue = None
  
  edges = data.get("data", {}).get("search", {}).get("edges", [])
  for edge in edges:
    node = edge.get("node", {})
    if not node:
      continue
    title = node.get("title", "")
    url = node.get("url", "")
    original_question = node.get("body", "")
    github_number=node.get("number")
    closed_at= node.get("closedAt")
    
    open_issue = FetchedIssue(
      github_number=github_number,
      title=title,
      url=url,
      original_question=original_question,
      closed_at=closed_at,
      tags=_labels(node),
    )
  return open_issue


CLOSED_ISSUES_QUERY="""
query($cursor:String, $owner:String!, $name:String!){
  repository(owner:$owner, name:$name){
    issues(first:100, after:$cursor, states:CLOSED, orderBy:{field:CREATED_AT, direction:DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number
        title
        url
        body
        closedAt
        labels(first:10) { nodes { name } }
        timelineItems(itemTypes:[CLOSED_EVENT], last:1) {
          nodes { ... on ClosedEvent { closer { ... on PullRequest { body } } } }
        }
        comments(last:1) { nodes { body } }
      }
    }
  }
  rateLimit { cost remaining resetAt }
}
"""


_NOISE_MARKERS = (
    "please follow",
    "issue template",
    "duplicate of",
    "can you provide",
    "please provide",
    "reproducible example",
    "minimal reproducible",
    "more information",
    "more info",
    "closing this as",
    "closing as stale",
    "is this still",
    "issue manager",
    "automatically closed",
    "assuming the original need",
)


def _labels(node: dict) -> list[str]:
    return [n.get("name", "") for n in (node.get("labels") or {}).get("nodes", [])]


def _looks_like_fix(text: str) -> bool:
    t = (text or "").strip()
    if len(t) < 40:
        return False
    low = t.lower()
    return not any(marker in low for marker in _NOISE_MARKERS)


def _node_to_fetched_issue(node: dict) -> FetchedIssue:
    title = node.get("title") or ""
    url = node.get("url") or ""
    original_question = node.get("body") or ""
    github_number = node.get("number")
    closed_at = node.get("closedAt")

    fix_summary = ""
    timeline_nodes = (node.get("timelineItems") or {}).get("nodes", [])
    if timeline_nodes:
        closer = timeline_nodes[0].get("closer") or {}
        fix_summary = closer.get("body") or ""

    if not fix_summary:
        comment_nodes = (node.get("comments") or {}).get("nodes", [])
        if comment_nodes:
            candidate = comment_nodes[0].get("body") or ""
            if _looks_like_fix(candidate):
                fix_summary = candidate

    return FetchedIssue(
        github_number=github_number,
        title=title,
        url=url,
        original_question=original_question,
        closed_at=closed_at,
        fix_summary=fix_summary,
        tags=_labels(node),
    )


def fetch_closed_issues_page(token: str, cursor: str | None = None):
  resp = requests.post(
    "https://api.github.com/graphql",
    json={"query": CLOSED_ISSUES_QUERY, "variables": {"cursor": cursor, "owner": REPO_OWNER, "name": REPO_NAME}},
    headers={"Authorization": f"Bearer {token}"},
  )
  resp.raise_for_status()
  body = resp.json()
  if body.get("errors"):
    raise RuntimeError(f"GitHub GraphQL error: {body['errors']}")
  payload = body["data"]

  conn = payload["repository"]["issues"]
  page_info = conn["pageInfo"]
  issues = [_node_to_fetched_issue(n) for n in conn["nodes"]]
  return issues, page_info["endCursor"], page_info["hasNextPage"], payload["rateLimit"]

