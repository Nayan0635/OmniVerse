from google import genai
from openai import OpenAI
import _config

_gemini = genai.Client(api_key=_config.GEMINI_API_KEY) if _config.EMBEDDING_PROVIDER == "gemini" else None
_openai = OpenAI(api_key=_config.OPENAI_API_KEY) if _config.EMBEDDING_PROVIDER == "openai" else None

def embed(text: str) -> list[float]:
    if _config.EMBEDDING_PROVIDER == "gemini":
        resp = _gemini.models.embed_content(
            model=_config.EMBEDDING_PROVIDER, contents=text
        )
        return resp.embeddings[0].values
    else:
        resp = _openai.embeddings.create(
            model=_config.EMBEDDING_PROVIDER, input=text
        )
        return resp.data[0].embedding
