# src/tools/search_tool.py
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from src.configs import tavily_key

# Initialize the Tavily client
tavily_client = TavilyClient(api_key=tavily_key)


def search_competitor(query: str, max_results: int = 3) -> list:
    """
    Executes a web search optimized for LLM consumption.
    Returns a list of dicts containing title, url, and a short snippet.
    """
    try:
        response = tavily_client.search(
            query=query, search_depth="advanced", max_results=max_results
        )
        results = response.get("results", [])
        return [
            {"title": r.get("title"), "url": r.get("url"), "snippet": r.get("content")}
            for r in results
        ]
    except Exception as e:
        print(f"Error during search execution: {e}")
        return []


def scrape_url_content(url: str) -> str:
    """
    Fetches a webpage, strips out scripts/styles, and extracts readable text.
    Acts as a fallback or deep-dive mechanism when simple search snippets aren't enough.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return (
                f"Failed to retrieve page content. Status Code: {response.status_code}"
            )

        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Strip headers, footers, scripts, and navigation links to save context tokens
        for element in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            element.decompose()

        # Get text and clean up whitespace
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        cleaned_text = "\n".join(lines)

        # Limit return length to avoid overwhelming the LLM in a single pass (roughly 4000 words)
        return cleaned_text[:16000]

    except Exception as e:
        return f"An error occurred while scraping the URL: {e}"
