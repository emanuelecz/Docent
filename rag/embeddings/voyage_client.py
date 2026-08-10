from functools import lru_cache
from voyageai import Client
from dotenv import load_dotenv
import os

load_dotenv()

VOYAGEAI_API_KEY = os.getenv("VOYAGEAI_API_KEY")


@lru_cache
def get_embedding_client() -> Client:
    return Client(api_key=VOYAGEAI_API_KEY)
