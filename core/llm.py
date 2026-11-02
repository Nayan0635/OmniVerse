import _config

_provider = _config.LLM_PROVIDER
_model = _config.CHAT_MODELS

if _provider == "gemini":
    from langchain_google_genai import ChatGoogleGenerativeAI
    _llm = ChatGoogleGenerativeAI(
        model=_model,
        google_api_key=_config.GEMINI_API_KEY,
    )
elif _provider == "nvidia":
    from langchain_nvidia_ai_endpoints import ChatNVIDIA
    _llm = ChatNVIDIA(
        model=_model,
        api_key=_config.NVIDIA_API_KEY,
    )
elif _provider == "openai":
    from langchain_openai import ChatOpenAI
    _llm = ChatOpenAI(
        model=_model,
        api_key=_config.OPENAI_API_KEY,
    )
else:
    raise ValueError(f"Unsupported LLM provider: {_provider}")


def ask(context: str, question: str) -> str:
    prompt = f"""You are answering questions using ONLY the context below.

    Context (each block is tagged with its source, e.g. [file.pdf § 3]): {context}
    Question: {question}

    Rules:
    - Answer using only the context above.
    - After each fact, cite the block(s) it came from using the same tag format: [file.pdf § 3].
    - If two files both contribute, cite both.
    - If the answer is not present in the context, say "I don't know".
    """

    resp = _llm.invoke(prompt)
    return resp.content
