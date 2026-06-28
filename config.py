# config.py
# Central place to load settings for the Ad Generation Pipeline.
# Import from here so secrets aren't scattered everywhere.

import os
from dotenv import load_dotenv

load_dotenv()

# --- Ollama settings (local LLM) ---
OLLAMA_MODEL = "llama3"
OLLAMA_BASE_URL = "http://localhost:11434"

# --- Hugging Face settings (cloud image generation) ---
HF_TOKEN = os.getenv("HF_TOKEN")

IMAGE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"

# --- ChromaDB settings (local memory) ---
CHROMA_PATH = "chroma_db"
