import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from openai import OpenAI

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

text = "Testing document embeddings."

def test_gemini():
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=key) if key else genai.Client()
    client = genai.Client()
    return client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    ).embeddings[0].values

def test_openai():
    client = OpenAI()
    return client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    ).data[0].embedding

def test_nvidia():
    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=os.getenv("NVIDIA_API_KEY")
    )
    return client.embeddings.create(
        model="nvidia/nemotron-3.5-embed-1b",
        input=text,
        extra_body={"input_type": "query"}
    ).data[0].embedding

models = {
    "Gemini": test_gemini,
    "OpenAI": test_openai,
    "NVIDIA": test_nvidia
}

for name, test in models.items():
    try:
        embedding = test()
        print(f"✅ {name}: Active | Dimensions: {len(embedding)}")
    except Exception as e:
        print(f"❌ {name}: Failed | {e}")
