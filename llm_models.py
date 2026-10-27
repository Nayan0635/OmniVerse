import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from openai import OpenAI

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

# Change these two values to test another model
PROVIDER = "gemini"
MODEL = "gemini-3.1-flash-lite"

prompt = "Reply with exactly: Model is working!"

def test_model(provider, model):
    if provider == "gemini":
        key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        client = genai.Client(api_key=key) if key else genai.Client()

        response = client.models.generate_content(
            model=model,
            contents=prompt
        )
        return response.text

    elif provider == "openai":
        client = OpenAI()

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    elif provider == "nvidia":
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.getenv("NVIDIA_API_KEY")
        )
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    else:
        raise ValueError(f"Unsupported provider: {provider}")

try:
    result = test_model(PROVIDER, MODEL)

    if result and result.strip():
        print(f"✅ {PROVIDER} | {MODEL} | {result.strip()}")
    else:
        print(f"⚠️ {PROVIDER} | {MODEL}: Request succeeded, but response was empty")

except Exception as e:
    print(f"❌ {PROVIDER} | {MODEL}: Failed")
    print(f"Reason: {e}")
