import os
from dotenv import load_dotenv
load_dotenv()

# Provider: "gemini" 
PROVIDER = "gemini"

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

EMBED_MODEL = {
    "gemini": "gemini-embedding-001",
    # "gemini": "gemini-embedding-002",
    "openai": "text-embedding-3-small",
}[PROVIDER]

CHAT_MODEL = {
    "gemini": "gemini-3.1-flash-lite",
    "openai": "gpt-4.1-mini",
}[PROVIDER]

CHROMA_PATH = "./database"
COLLECTION_NAME = "documents"