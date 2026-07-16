from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

from .env import api_key, base_url, model, mode


def get_llm():
    if mode.lower() == "ollama":
        return ChatOllama(
            model=model,
            base_url=base_url,
        )

    return ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=base_url,
    )


llm = get_llm()
