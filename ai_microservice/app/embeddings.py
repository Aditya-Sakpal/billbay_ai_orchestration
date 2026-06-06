import asyncio
from functools import lru_cache

from app.config import get_settings


@lru_cache(maxsize=1)
def _get_local_model():
    from sentence_transformers import SentenceTransformer

    settings = get_settings()
    return SentenceTransformer(settings.local_embedding_model)


async def embed_text(text: str) -> list[float]:
    """
    Embed a single string. Returns a list of floats.
    Uses local sentence-transformers by default.
    Falls back to OpenAI if EMBEDDING_PROVIDER=openai.
    """
    settings = get_settings()

    if settings.embedding_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required when EMBEDDING_PROVIDER=openai"
            )
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return response.data[0].embedding

    model = _get_local_model()
    embedding = await asyncio.to_thread(
        model.encode,
        text,
        normalize_embeddings=True,
    )
    return embedding.tolist()


def get_embedding_dimension() -> int:
    """Returns the dimension for the current provider."""
    settings = get_settings()
    if settings.embedding_provider == "openai":
        return 1536
    return 384
