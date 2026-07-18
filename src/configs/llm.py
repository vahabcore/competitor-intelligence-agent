from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

from .env import api_key, base_url, model, mode, smart_llm_model


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


def get_smart_llm_model():
    if mode.lower() == "ollama":
        return ChatOllama(model=smart_llm_model, base_url=base_url, streaming=True)

    return ChatOpenAI(
        model=smart_llm_model, api_key=api_key, base_url=base_url, streaming=True
    )


llm = get_llm()
smart_llm = get_smart_llm_model()
