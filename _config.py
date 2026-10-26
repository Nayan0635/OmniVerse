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
    # "nvidia": "nemotron-3.5-embed-1b",
    # "nvidia": "nemotron-3.5-embed-8b",
    "openai": "text-embedding-3-small",
}[EMBED_PROVIDER]

# Chat models
chat_model = {
    "gemini": "gemini-3.1-flash-lite",
    "openai": "gpt-4.1-mini",
    # Add your preferred NVIDIA chat model here
}[CHAT_PROVIDER]

# Database configuration
CHROMA_PATH = "./database"
COLLECTION_NAME = "documents"