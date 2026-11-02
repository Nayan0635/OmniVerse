import _config

_provider = _config.EMBEDDING_PROVIDER
_model = _config.EMBEDDING_MODELS

if _provider == "gemini":
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    _embedder = GoogleGenerativeAIEmbeddings(
        model=_model,
        google_api_key=_config.GEMINI_API_KEY,
    )
elif _provider == "nvidia":
    from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
    # Two instances: one for queries, one for passages (documents).
    # NVIDIA requires the input_type distinction for optimal retrieval.
    _embedder_query = NVIDIAEmbeddings(
        model=_model,
        api_key=_config.NVIDIA_API_KEY,
        input_type="query",
    )
    _embedder_passage = NVIDIAEmbeddings(
        model=_model,
        api_key=_config.NVIDIA_API_KEY,
        input_type="passage",
    )
elif _provider == "openai":
    from langchain_openai import OpenAIEmbeddings
    _embedder = OpenAIEmbeddings(
        model=_model,
        api_key=_config.OPENAI_API_KEY,
    )
else:
    raise ValueError(f"Unsupported embedding provider: {_provider}")


def embed(text: str, input_type: str = "query") -> list[float]:
    if _provider == "nvidia":
        emb = _embedder_passage if input_type == "passage" else _embedder_query
    else:
        emb = _embedder

    if input_type == "passage":
        return emb.embed_documents([text])[0]
    return emb.embed_query(text)
