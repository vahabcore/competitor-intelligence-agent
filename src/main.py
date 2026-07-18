from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json
import os
import shutil

from src.agents.graph import build_competitor_graph
from src.tools.vector_db_tool import (
    ingest_document,
    list_ingested_sources,
    delete_source,
    UPLOADS_DIR,
)

app = FastAPI(title="Competitor Intelligence Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResearchRequest(BaseModel):
    competitor_name: str
    user_request: Optional[str] = "General Analysis"



agent_app = build_competitor_graph()
config = {"configurable": {"thread_id": "api_session_1"}}


def extract_content(chunk_content) -> str:
    """Safely extract text from chunk.content which can be str or list."""
    if isinstance(chunk_content, str):
        return chunk_content
    if isinstance(chunk_content, list):
        parts = []
        for item in chunk_content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(item["text"])
        return "".join(parts)
    return ""


@app.post("/api/research")
async def run_research(request: ResearchRequest):
    async def event_stream():
        initial_state = {
            "competitor_name": request.competitor_name,
            "user_request": request.user_request,
            "revision_count": 0,
        }

        # Helper to send an SSE message with proper newlines
        def sse(payload: dict) -> str:
            return f"data: {json.dumps(payload)}\n\n"

        try:
            # Send a "started" status event immediately
            yield sse({"node": "start", "status": f"🚀 Starting analysis for **{request.competitor_name}**..."})

            async for event in agent_app.astream_events(
                initial_state, config=config, version="v2"
            ):
                kind = event["event"]
                name = event.get("name", "")
                tags = event.get("tags", [])

                # Node lifecycle events — send status updates
                if kind == "on_chain_start":
                    if name == "researcher":
                        yield sse({"node": name, "status": f"\n\n---\n\n🔍 **Researcher** — Searching web for *{request.competitor_name}*...\n\n"})
                    elif name == "internal_analyst":
                        yield sse({"node": name, "status": "\n\n📂 **Internal Analyst** — Querying internal knowledge base...\n\n"})
                    elif name == "strategist":
                        yield sse({"node": name, "status": "\n\n---\n\n⚙️ **Strategist** — Drafting battlecard...\n\n"})
                    elif name == "critic":
                        yield sse({"node": name, "status": "\n\n🔎 **Critic** — Reviewing draft...\n\n"})

                # LLM streaming tokens
                elif kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    text = extract_content(chunk.content)
                    if text:
                        yield sse({"chunk": text})

                # Node completion events
                elif kind == "on_chain_end":
                    output = event.get("data", {}).get("output", {})
                    if not isinstance(output, dict):
                        continue

                    if name == "researcher" and output.get("research_data"):
                        yield sse({
                            "research": True,
                            "source": "web",
                            "title": "🔍 Web Research",
                            "content": output["research_data"],
                        })

                    elif name == "internal_analyst" and output.get("internal_data"):
                        yield sse({
                            "research": True,
                            "source": "internal",
                            "title": "📂 Internal Knowledge Base",
                            "content": output["internal_data"],
                        })

                    elif name == "critic" and output.get("final_report"):
                        yield sse({"node": "done", "status": "\n\n✅ **Analysis complete!**\n\n"})

        except Exception as e:
            yield sse({"error": str(e)})

        # Signal stream end
        yield sse({"done": True})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/ingest/upload")
async def upload_document(file: UploadFile = File(...)):
    """Accept a PDF or markdown file from the browser, save it, and ingest into ChromaDB."""
    allowed_extensions = {".pdf", ".md", ".txt", ".markdown"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: PDF, MD, TXT.",
        )

    dest_path = os.path.join(UPLOADS_DIR, file.filename)

    # Save file to disk
    try:
        with open(dest_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # Ingest into ChromaDB
    try:
        chunks = ingest_document(dest_path)
        return {
            "message": f"Successfully ingested '{file.filename}' ({chunks} chunks).",
            "name": file.filename,
            "chunks": chunks,
        }
    except Exception as e:
        # Clean up saved file if ingestion failed
        if os.path.exists(dest_path):
            os.remove(dest_path)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ingest/documents")
async def list_documents():
    """Return a list of all ingested source documents."""
    try:
        sources = list_ingested_sources()
        return {"documents": sources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/ingest/documents/{source_name}")
async def delete_document(source_name: str):
    """Delete all chunks for a given source file from ChromaDB and remove the file."""
    try:
        deleted = delete_source(source_name)
        return {"message": f"Deleted '{source_name}' ({deleted} chunks removed)."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

