from voyageai import Client
from dotenv import load_dotenv
import os
load_dotenv()

VOYAGEAI_API_KEY= os.getenv("VOYAGEAI_API_KEY")

def get_embedding_client():
    client = Client(api_key=VOYAGEAI_API_KEY)
    return client