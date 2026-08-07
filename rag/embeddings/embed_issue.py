from voyageai import Client

def embed_issue_text(client: Client,text: str = "") ->list[float]:
    if not text:
        raise ValueError("Cannot embedd an empty string")
    result = client.embed([text], model="voyage-4", input_type="document")
    return result.embeddings[0]

def issue_embed_text(issue) -> str:
    return f"Title: {issue.title}\n Question:  {issue.original_question}"


def embed_texts(client:Client, texts: list[str], batch_size:int=128)-> list[list[float]]:
    if not texts:
        raise ValueError("Cannot embedd an empty list")
    vectors = []
    for i in range(0, len(texts), batch_size):
        chunk = texts[i:i + batch_size]
        result = client.embed(
            chunk,
            model="voyage-4",
            input_type="document",
            output_dimension=1024
        )
        vectors.extend(result.embeddings)
    return vectors
    