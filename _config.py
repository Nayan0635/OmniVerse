# choose provider manually as you wish
import os
from dotenv import load_dotenv

load_dotenv()

# Select providers independently
EMBED_PROVIDER = "gemini"
CHAT_PROVIDER = "openai"

# API keys
# NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Embedding models
embed_model = {
    "gemini": "gemini-embedding-001",
    # "gemini": "gemini-embedding-002",
    "nvidia": "nemotron-3.5-embed-1b",
    # "nvidia": "nemotron-3.5-embed-8b",
    "openai": "text-embedding-3-small",
}[EMBED_PROVIDER]

# Chat models
chat_model = {
    "gemini": "gemini-3.1-flash-lite",
    "openai": "gpt-4.1-mini",
    "nvidia": "meta/muse-glimmer-30b",
    "nvidia": "z-ai/glm-5.3",
    "nvidia": "nvidia/nemotron-3-ultra-550b-a55b",
    "nvidia": "nvidia/nemotron-3.5-super-vl-120b-a12b",
    "groq": "groq/compound-mini", # 21 Sep 2026
    "groq": "openai/gpt-oss-120b",
    "groq": "qwen/qwen3.8-27b"
}[CHAT_PROVIDER]

# Database configuration
CHROMA_PATH = "./database"
COLLECTION_NAME = "documents"