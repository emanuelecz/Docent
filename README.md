# Backend

AI-powered triage service for open-source GitHub issues. It ingests issues,
runs them through an agent pipeline, and drafts responses grounded in a
retrieval corpus.

## Stack

- **FastAPI** — HTTP API
- **Celery + Redis** — background workers and scheduled polling
- **PostgreSQL + pgvector** — data store and vector search
- **SQLAlchemy + Alembic** — ORM and migrations
- **LangChain / LangGraph** — agent orchestration
- **Anthropic / OpenAI / Voyage** — LLMs and embeddings

## Layout

| Path          | Purpose                                                     |
| ------------- | ---------------------------------------------------------- |
| `api/`        | FastAPI app, routes, CRUD, and services                    |
| `agent/`      | Agent pipeline: intake → gate → research → draft → escalate |
| `rag/`        | Chunking, embeddings, and retrieval                        |
| `ingestion/`  | GitHub issue ingestion                                     |
| `workers/`    | Celery app and tasks (issue polling, corpus backfill)      |
| `database/`   | Engine, models, and session management                     |
| `migrations/` | Alembic migration scripts                                  |
| `mcp/`        | MCP client and server                                      |

## Getting started

Dependencies are managed with [uv](https://github.com/astral-sh/uv).

```bash
uv sync
```

Create a `.env` file with the required secrets (database URL, Redis URL,
GitHub token, and LLM API keys).

Run database migrations:

```bash
uv run alembic upgrade head
```

Start the API:

```bash
uv run uvicorn api.server:app --reload
```

Start the workers:

```bash
uv run celery -A workers.celery_app worker --beat
```

## Docker

The full stack (Postgres, Redis, API, workers, frontend) is defined in the
root `docker-compose.yml`:

```bash
docker compose up
```
