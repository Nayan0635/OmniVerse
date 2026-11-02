import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

# Change these two values to test another model.
PROVIDER = "gemini"
MODEL = "gemini-embedding-001"

text = "Testing document embeddings."

def test_model(provider: str, model: str) -> list[float]:
    if provider == "gemini":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        embedder = GoogleGenerativeAIEmbeddings(
            model=model,
            google_api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
        )
        return embedder.embed_query(text)

    elif provider == "openai":
        from langchain_openai import OpenAIEmbeddings

        embedder = OpenAIEmbeddings(
            model=model,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        return embedder.embed_query(text)

    elif provider == "nvidia":
        from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings

        embedder = NVIDIAEmbeddings(
            model=model,
            api_key=os.getenv("NVIDIA_API_KEY"),
            input_type="query",
        )
        return embedder.embed_query(text)

    else:
        raise ValueError(f"Unsupported provider: {provider}")


if __name__ == "__main__":
    try:
        embedding = test_model(PROVIDER, MODEL)
        print(f"✅ {PROVIDER} | {MODEL}: Active")
        print(f"Dimensions: {len(embedding)}")

    except Exception as e:
        print(f"❌ {PROVIDER} | {MODEL}: Failed")
        print(f"Reason: {e}")
