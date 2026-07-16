import os
from dotenv import load_dotenv

load_dotenv()

mode = os.getenv("LLM_MODE", "ollama")
model = os.getenv("LLM_MODEL")
base_url = os.getenv("LLM_BASE_URL")
api_key = os.getenv("LLM_API_KEY")
tavily_key = os.getenv("TAVILY_API_KEY")
chroma_db_dir = os.getenv("CHROMA_DB_DIR", "./data/chroma_db")


if not api_key:
    raise ValueError("OPENAI_API_KEY is missing from the environment configuration.")
