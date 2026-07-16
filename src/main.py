from configs.llm import llm
from tools.convert_vector import ingest_document, query_internal_data

# from helpers.dir_helpers import RAW_DOCS
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DOCS = DATA_DIR / "raw_internal_docs"
VECTOR_DB = PROJECT_ROOT / "chroma_db"

if __name__ == "__main__":
    test_file_path = RAW_DOCS / "raw_internal_docs.md"

    if not test_file_path.exists():
        raise FileNotFoundError(f"File not found:\n{test_file_path}")

    # Run Ingestion
    ingest_document(test_file_path)

    # Run a Test Query
    print("\n--- Testing ChromaDB Retrieval ---")

    query = "What are the limitations and weaknesses of Acme?"
    matches = query_internal_data(query)

    for i, match in enumerate(matches, start=1):
        print(f"\nMatch {i} (Source: {match.metadata.get('source')})")
        print(match.page_content)
