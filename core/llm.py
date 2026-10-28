from google import genai
from openai import OpenAI
import _config

_provider = _config.LLM_PROVIDER

_gemini = genai.Client(api_key=_config.GEMINI_API_KEY) if _provider == "gemini" else None
_openai = OpenAI(api_key=_config.OPENAI_API_KEY) if _provider == "openai" else None
_nvidia = (OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=_config.NVIDIA_API_KEY) if _provider == "nvidia" else None)


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

    if _provider == "gemini":
        resp = _gemini.models.generate_content(
            model=_config.CHAT_MODELS,
            contents=prompt,
        )
        return resp.text

    elif _provider in ("openai", "nvidia"):
        client = _openai if _provider == "openai" else _nvidia

        resp = client.chat.completions.create(
            model=_config.CHAT_MODELS,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
        return resp.choices[0].message.content

    else:
        raise ValueError(f"Unsupported LLM provider: {_provider}")