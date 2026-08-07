from fastapi import FastAPI
from api.routes.fetch_issue import router as fetch_router
from api.routes.corpus_backfill import router as corpus_backfill_router
from database.db import Base, sync_engine

Base.metadata.create_all(bind=sync_engine)
app = FastAPI()

app.include_router(fetch_router)
app.include_router(corpus_backfill_router)
