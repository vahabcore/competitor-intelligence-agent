import os
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter
from configs import api_key, chroma_db_dir

HEADERS_TO_SPLIT_ON = [
    ("#", "Header_1"),
    ("##", "Header_2"),
]


def get_vector_store() -> Chroma:
    """Returns the Chroma vector store instance."""
    embeddings = OllamaEmbeddings(
        model="llama3.1:8b",
    )
    return Chroma(
        persist_directory=chroma_db_dir,
        embedding_function=embeddings,
        collection_name="internal_company_data",
    )


def ingest_document(file_path: str):
    """Reads a markdown file, splits it by headers, and saves it to ChromaDB."""
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split the Markdown by headers to preserve semantic meaning per section
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADERS_TO_SPLIT_ON
    )
    docs = markdown_splitter.split_text(content)

    # Add standard metadata
    for doc in docs:
        doc.metadata["source"] = os.path.basename(file_path)

    # Initialize vector store and save documents
    vector_store = get_vector_store()
    vector_store.add_documents(docs)
    print(f"Successfully ingested {len(docs)} chunks from {file_path} into ChromaDB.")


def query_internal_data(query: str, k: int = 2):
    """Queries ChromaDB to find matching context for a given prompt."""
    vector_store = get_vector_store()
    results = vector_store.similarity_search(query, k=k)
    return results


ingest_document_fn = ingest_document
query_internal_data_fn = query_internal_data
