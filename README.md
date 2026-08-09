# Docent — Backend

Docent is an AI triage service for open-source GitHub repositories. It watches a
repo's issues, keeps a searchable corpus of **already-resolved** issues, and —
on demand — runs an open issue through a retrieval-augmented agent that drafts a
grounded response citing how similar problems were solved before.

The reference target is [`pydantic/pydantic`](https://github.com/pydantic/pydantic),
configurable via `REPO_OWNER` / `REPO_NAME`.

---

## How it works

Docent keeps **two stores** that play opposite roles:

- **Corpus** (`closed-issues`) — closed issues that were *actually solved*, each
  with the original question, the fix, and an embedding. This is the knowledge
  the agent retrieves *from*.
- **Queue** (`open-issues`) — the currently-open issues shown on the dashboard,
  the ones you can run the agent *on*.

```
                          GitHub
             closed issues │ open issues
        ┌──────────────────┼──────────────────┐
        ▼                                      ▼
  closed-issues poller (5m)            open-issues poller (30m)
  backfill (one-shot)                  diff GitHub vs queue
        │                              ├─ new  → insert into queue
        ▼                              └─ gone → promote to corpus
   ┌─────────────┐   retrieve      ┌─────────────┐
   │   CORPUS    │◄────────────────│    QUEUE    │
   │ closed-     │   promote on    │  open-      │
   │ issues      │   resolution    │  issues     │
   └─────┬───────┘                 └─────┬───────┘
         │ hybrid search + rerank        │ "Run Agent"
         ▼                               ▼
   ┌──────────────────────────────────────────────┐
   │  Agent:  intake → research → draft            │
   │          (→ gate → escalate, planned)         │
   └──────────────────────────────────────────────┘
```

### Lifecycle of an issue

1. Opened on GitHub → the open-issues poller inserts it into the **queue**.
2. It shows on the dashboard; a user clicks **Run Agent**.
3. **Intake** summarizes the body and embeds `title + question`; **research**
   runs hybrid retrieval over the corpus, reranks, and (when needed) calls tools
   via MCP; **draft** writes a grounded answer.
4. Later the issue is closed on GitHub → the poller notices it left the open set,
   fetches the real fix, and if it's a genuine resolution **promotes it into the
   corpus** (and drops it from the queue). The corpus is now a little smarter for
   the next question.

---

## Stack

| Concern            | Tool                                            |
| ------------------ | ----------------------------------------------- |
| HTTP API           | **FastAPI** + Uvicorn                           |
| Background jobs    | **Celery** + **Redis** (broker & scheduler)     |
| Data + vectors     | **PostgreSQL** + **pgvector**                   |
| ORM & migrations   | **SQLAlchemy 2.0** + **Alembic**                |
| Agent orchestration| **LangChain / LangGraph** *(in progress)*       |
| Generation         | **Anthropic** (drafts, summaries)               |
| Embeddings & rerank| **Voyage AI**                                   |
| Tooling            | **MCP** client/server *(planned)*               |

---

## Project layout

| Path                     | Purpose                                                          |
| ------------------------ | --------------------------------------------------------------- |
| `api/`                   | FastAPI app, routes, CRUD                                        |
| `api/server.py`          | App entrypoint (`api.server:app`)                               |
| `ingestion/issues.py`    | GitHub GraphQL fetchers (open, closed, by-number) + fix parsing  |
| `rag/embeddings/`        | Voyage client and issue → embedding helpers                     |
| `rag/ingestion/`         | Closed-issue promotion into the corpus                          |
| `workers/celery_app.py`  | Celery app + beat schedules                                     |
| `workers/tasks/`         | Pollers (open, closed) and corpus backfill                     |
| `database/models/`       | `ClosedIssue`, `OpenIssue`                                       |
| `database/db.py`         | Engine, `SessionLocal`, `Base`                                   |
| `schemas/`               | Pydantic DTOs (`FetchedIssue`, `IssueCreate`, `PreparedIssue`)   |
| `migrations/`            | Alembic environment and versions                                |
| `core/config.py`         | Typed settings loaded from the environment                      |
| `agent/`                 | Agent stages: intake → research → draft → gate → escalate *(WIP)* |
| `mcp/`                   | MCP client/server *(planned)*                                   |

---

## Data model

**`closed-issues`** — the retrieval corpus (one row per resolved issue):

| Column              | Notes                                             |
| ------------------- | ------------------------------------------------- |
| `github_number`     | unique                                            |
| `title`             |                                                   |
| `original_question` | the issue body                                    |
| `fix_summary`       | how it was resolved (closing PR / comment)        |
| `url`, `closed_at`  |                                                   |
| `tags`              | GitHub labels                                     |
| `embeddings`        | `vector(1024)` over `title + original_question`   |

**`open-issues`** — the work queue (one row per open issue):

| Column              | Notes                                             |
| ------------------- | ------------------------------------------------- |
| `github_number`     | unique                                            |
| `title`, `original_question`, `url`, `tags` | filled at sync time          |
| `body_summary`      | nullable — filled lazily at intake                |
| `embeddings`        | `vector(1024)`, nullable — filled lazily at intake |

Embeddings/summaries are left empty by the poller and computed only when the
agent actually runs on an issue, so the corpus is embedded exactly once and open
issues are embedded only if someone works on them.

---

## Background jobs

Configured in `workers/celery_app.py`:

| Task                 | Schedule      | Does                                                        |
| -------------------- | ------------- | ---------------------------------------------------------- |
| `poll_github_issues` | every 5 min   | Pull newly *closed* issues with a fix into the corpus       |
| `poll_open_issues`   | every 30 min  | Sync the open-issues queue; promote resolved ones to corpus |
| `backfill_corpus_page` | on demand   | One-shot historical backfill of the closed-issue corpus     |

Run the worker and scheduler together (`worker --beat`) or as separate
processes (`worker`, `beat`) — the compose stack runs them separately.

---

## API

| Method & path              | Purpose                                            |
| -------------------------- | -------------------------------------------------- |
| `POST /issues/fetch`       | Fetch the latest open issue from GitHub            |
| `POST /admin/corpus/backfill?limit=1500` | Kick off the corpus backfill (async)  |

---

## Getting started

### Docker (self-contained)

This repo ships its own `docker-compose.yml` — Postgres (pgvector), Redis, the
API, and the Celery worker + beat. From a fresh clone:

```bash
cp .env.example .env          # then fill in your API keys
docker compose up --build     # api :8000 · postgres :5433 · redis :6379
docker compose run --rm backend uv run alembic upgrade head   # first-time schema
```

The `postgres` service auto-creates the pgvector extension from `db/init/`, and
`DATABASE_URL` / `REDIS_URL` are wired to the compose services (overriding
whatever is in `.env`, which is used only when running on the host).

### Local (uv)

Dependencies are managed with [uv](https://github.com/astral-sh/uv). You still
need a reachable Postgres (with pgvector) and Redis — the compose above is the
easiest way to get them.

```bash
uv sync
cp .env.example .env          # fill in secrets + point DATABASE_URL/REDIS_URL at your services
uv run alembic upgrade head
uv run uvicorn api.server:app --reload           # API on :8000
uv run celery -A workers.celery_app.app worker --beat --loglevel=info   # workers
```

---

## Configuration

All settings are read from the environment (see `.env.example`) and validated in
`core/config.py`.

| Variable              | Required | Purpose                                    |
| --------------------- | -------- | ------------------------------------------ |
| `GITHUB_PAT_KEY`      | yes      | GitHub token for the GraphQL API           |
| `REPO_OWNER` / `REPO_NAME` | yes | Repository to triage                       |
| `ANTHROPIC_API_KEY`   | yes      | Drafts and summaries                       |
| `VOYAGEAI_API_KEY`    | yes      | Embeddings and reranking                   |
| `OPENAI_API_KEY`      | optional | Reserved for alternate models              |
| `DATABASE_URL`        | yes      | Postgres connection (host-facing)          |
| `REDIS_URL`           | yes      | Celery broker / backend                    |

---

## Database & migrations

Schema changes go through Alembic; never rely on autogenerate blindly against a
populated database (it will try to drop renamed tables). Migrations live in
`migrations/versions/`.

```bash
uv run alembic upgrade head          # apply
uv run alembic revision -m "..."     # new revision (hand-edit for renames)
uv run alembic downgrade -1          # roll back one
```

The `embeddings` (pgvector) column is excluded from autogenerate diffs in
`migrations/env.py`.

---

## Status

**Working:** issue ingestion (open + closed), the corpus with hybrid-search-ready
embeddings, the polling/backfill jobs, and the open↔closed lifecycle.

**In progress / planned:** the agent stages (`intake → research → draft`), the
`gate`/`escalate` steps, MCP tools, a runs/eval table for drafts and
draft-vs-real-fix comparisons, and the dashboard frontend.
