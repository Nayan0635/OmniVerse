from google import genai
from openai import OpenAI
import _config

_provider = _config.EMBEDDING_PROVIDER

_gemini = genai.Client(api_key=_config.GEMINI_API_KEY) if _provider == "gemini" else None
_openai = OpenAI(api_key=_config.OPENAI_API_KEY) if _provider == "openai" else None
_nvidia = (OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=_config.NVIDIA_API_KEY) if _provider == "nvidia" else None)

def embed(text: str, input_type: str = "query") -> list[float]:
    if _provider == "gemini":
        resp = _gemini.models.embed_content(
            model=_config.EMBEDDING_MODELS, contents=text
        )
        return resp.embeddings[0].values
    
    elif _provider == "openai":
        resp = _openai.embeddings.create(
            model=_config.EMBEDDING_MODELS,
            input=text,
        )
        return resp.data[0].embedding

    elif _provider == "nvidia":
        resp = _nvidia.embeddings.create(
            model=_config.EMBEDDING_MODELS,
            input=[text],
            extra_body={"input_type": input_type},
        )
        return resp.data[0].embedding

    else:
        raise ValueError(
            f"Unsupported embedding provider: {_provider}"
        )

    # if not embedding:
    #     raise ValueError("Embedding provider returned an empty vector")
