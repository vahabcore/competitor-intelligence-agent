# Competitor Intelligence Agent

An AI-powered multi-agent system that automates competitor research and transforms scattered web information into actionable business insights.

The agent combines web search, intelligent scraping, Retrieval-Augmented Generation (RAG), and multiple specialized AI agents to analyze competitors, compare them with internal product knowledge, and generate structured competitive battlecards. It delivers insights such as feature comparisons, pricing analysis, SWOT analysis, product gaps, and sales recommendations to help teams make informed strategic decisions.

Built with a production-focused architecture using **Python**, **LangGraph**, **ChromaDB**, **Playwright**, **Tavily**, and **OpenAI**.



## ✅ Phase 1 Completed: Core RAG (Local Knowledge Base)

Successfully completed the first phase of the Competitor Intelligence Agent by building the core Retrieval-Augmented Generation (RAG) pipeline.

### Completed Tasks

* Loaded the mock company's internal knowledge via .md file into **ChromaDB**, including:

  * sample text in raw_internal_docs.md.

* Implemented **semantic Markdown header-based chunking** to preserve document structure and context.

* Generated and stored vector embeddings for efficient semantic search.

* Configured a persistent **ChromaDB** vector store for local retrieval.

* Successfully tested semantic similarity search by retrieving the most relevant document chunks for user queries.

### Outcome

The project now has a fully functional local retrieval system capable of indexing internal documents and returning contextually relevant information. This forms the foundation for the next phase, where the retrieved context will be integrated with an LLM to generate intelligent, context-aware responses.
