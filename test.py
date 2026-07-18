import asyncio
from src.configs import llm, smart_llm
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    mode = os.getenv("LLM_MODE", "ollama")
    print(f"Testing current mode: {mode}")
    
    print("\nTesting llm...")
    try:
        res = llm.invoke("Hi")
        print(f"llm success: {res.content}")
    except Exception as e:
        print(f"llm error: {e}")

    print("\nTesting smart_llm...")
    try:
        res = smart_llm.invoke("Hi")
        print(f"smart_llm success: {res.content}")
    except Exception as e:
        print(f"smart_llm error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
