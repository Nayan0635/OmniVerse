import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

# Change these two values to test another model.
PROVIDER = "nvidia"
MODEL = "nvidia/nemotron-3.5-super-vl-120b-a12b"

prompt = "Reply with exactly: Model is working!"

def test_model(provider: str, model: str) -> str:
    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
        )

    elif provider == "openai":
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            model=model,
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    elif provider == "nvidia":
        from langchain_nvidia_ai_endpoints import ChatNVIDIA

        llm = ChatNVIDIA(
            model=model,
            api_key=os.getenv("NVIDIA_API_KEY"),
        )

    else:
        raise ValueError(f"Unsupported provider: {provider}")

    response = llm.invoke(prompt)
    return response.content


if __name__ == "__main__":
    try:
        result = test_model(PROVIDER, MODEL)

        if result and str(result).strip():
            print(f"✅ {PROVIDER} | {MODEL} | {str(result).strip()}")
        else:
            print(f"⚠️ {PROVIDER} | {MODEL}: Request succeeded, but response was empty")

    except Exception as e:
        print(f"❌ {PROVIDER} | {MODEL}: Failed")
        print(f"Reason: {e}")
