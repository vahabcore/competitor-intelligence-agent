import os
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from src.configs import chroma_db_dir

HEADERS_TO_SPLIT_ON = [
    ("#", "Header_1"),
    ("##", "Header_2"),
]

# Directory where uploaded PDFs/docs are saved on the server
UPLOADS_DIR = os.path.join(os.path.dirname(chroma_db_dir), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)


def get_vector_store() -> Chroma:
    """Returns the Chroma vector store instance."""
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text",
        base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434")
    )
    return Chroma(
        persist_directory=chroma_db_dir,
        embedding_function=embeddings,
        collection_name="internal_company_data_v2",
    )


def ingest_document(file_path: str) -> int:
    """
    Reads a file (PDF or Markdown), splits it into chunks, and stores them in ChromaDB.
    Returns the number of chunks ingested.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    source_name = os.path.basename(file_path)

    if ext == ".pdf":
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(file_path)
        raw_docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        docs = splitter.split_documents(raw_docs)
    else:
        # Treat as Markdown / plain text
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=HEADERS_TO_SPLIT_ON
        )
        docs = markdown_splitter.split_text(content)

    # Tag every chunk with a unique source identifier and doc_id
    for doc in docs:
        doc.metadata["source"] = source_name

    vector_store = get_vector_store()
    batch_size = 50
    for i in range(0, len(docs), batch_size):
        batch = docs[i : i + batch_size]
        vector_store.add_documents(batch)

    print(f"Ingested {len(docs)} chunks from '{source_name}' into ChromaDB.")
    return len(docs)


def list_ingested_sources() -> list[dict]:
    """
    Returns a list of unique source files that have been ingested,
    along with their chunk counts.
    """
    vector_store = get_vector_store()
    try:
        # Fetch all records — only metadatas needed, no embeddings
        result = vector_store.get(include=["metadatas"])
        metadatas = result.get("metadatas") or []
    except Exception:
        return []

    counts: dict[str, int] = {}
    for meta in metadatas:
        src = meta.get("source", "unknown")
        counts[src] = counts.get(src, 0) + 1

    sources = []
    for src, count in counts.items():
        file_path = os.path.join(UPLOADS_DIR, src)
        sources.append({
            "name": src,
            "chunks": count,
            "on_disk": os.path.exists(file_path),
        })
    return sources


def delete_source(source_name: str) -> int:
    """
    Deletes all ChromaDB documents for a given source file, and removes the
    file from the uploads directory. Returns the number of chunks deleted.
    """
    vector_store = get_vector_store()

    # Use the public where-filter to find only chunks belonging to this source
    try:
        result = vector_store.get(
            where={"source": source_name},
            include=["metadatas"],
        )
        ids_to_delete = result.get("ids") or []
    except Exception as e:
        raise RuntimeError(f"Failed to query ChromaDB: {e}")

    # Delete the matched chunks from ChromaDB
    if ids_to_delete:
        try:
            vector_store.delete(ids=ids_to_delete)
            print(f"Deleted {len(ids_to_delete)} chunks for '{source_name}' from ChromaDB.")
        except Exception as e:
            raise RuntimeError(f"Failed to delete from ChromaDB: {e}")
    else:
        print(f"No ChromaDB chunks found for source '{source_name}'.")

    # Remove the physical file from the uploads directory
    file_path = os.path.join(UPLOADS_DIR, source_name)
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Removed file from disk: {file_path}")

    return len(ids_to_delete)


def query_internal_data(query: str, k: int = 2):
    """Queries ChromaDB to find matching context for a given prompt."""
    vector_store = get_vector_store()
    results = vector_store.similarity_search(query, k=k)
    return results
