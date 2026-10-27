
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from openai import OpenAI

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

# Change these two values to test another model
PROVIDER = "gemini"
MODEL = "gemini-embedding-001"

text = "Testing document embeddings."

def test_model(provider, model):
    if provider == "gemini":
        key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        client = genai.Client(api_key=key) if key else genai.Client()

        return client.models.embed_content(
            model=model,
            contents=text
        ).embeddings[0].values

    elif provider == "openai":
        client = OpenAI()

        return client.embeddings.create(
            model=model,
            input=text
        ).data[0].embedding

    elif provider == "nvidia":
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.getenv("NVIDIA_API_KEY")
        )

        return client.embeddings.create(
            model=model,
            input=text,
            extra_body={"input_type": "query"}
        ).data[0].embedding

    else:
        raise ValueError(f"Unsupported provider: {provider}")

try:
    embedding = test_model(PROVIDER, MODEL)
    print(f"✅ {PROVIDER} | {MODEL}: Active")
    print(f"Dimensions: {len(embedding)}")

except Exception as e:
    print(f"❌ {PROVIDER} | {MODEL}: Failed")
    print(f"Reason: {e}")
