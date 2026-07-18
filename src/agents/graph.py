# src/agents/graph.py
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import ChatPromptTemplate
from src.tools.search_tool import search_competitor
from src.tools.vector_db_tool import query_internal_data
from .state import CompetitorIntelState
from src.configs import llm, smart_llm


def researcher_node(state: CompetitorIntelState):
    print(f"--- [Researcher] Searching web for {state['competitor_name']} ---")
    query = f"{state['competitor_name']} {state.get('user_request', 'new features pricing 2024')}"
    results = search_competitor(query, max_results=3)

    print("reasecher node ", results)
    formatted_research = "\n".join(
        [
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['snippet']}"
            for r in results
        ]
    )
    return {"research_data": formatted_research or "No recent data found."}


def internal_analyst_node(state: CompetitorIntelState):
    print(f"--- [Internal Analyst] Querying ChromaDB ---")
    query = f"Features and pricing to compare against {state['competitor_name']}"
    db_results = query_internal_data(query, k=3)
    print("reasecher node ", db_results)
    formatted_internal = "\n".join([doc.page_content for doc in db_results])
    return {"internal_data": formatted_internal}


def strategist_node(state: CompetitorIntelState):
    print("--- [Strategist] Drafting Battlecard (Please wait, generating...) ---")
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a B2B Competitive Strategist. Write a highly concise Markdown Battlecard comparing Acme to the competitor. Keep it under 400 words. Use short bullet points.",
            ),
            (
                "user",
                "Competitor: {competitor_name}\nUser Request: {user_request}\n\nResearch:\n{research_data}\n\nInternal Data:\n{internal_data}",
            ),
        ]
    )
    print("reasecher node ", state)
    response = (prompt | llm).invoke(
        {
            "competitor_name": state["competitor_name"],
            "user_request": state.get("user_request", "General Analysis"),
            "research_data": state.get("research_data", ""),
            "internal_data": state.get("internal_data", ""),
        }
    )

    return {"draft_report": response.content, "revision_count": 1}


def critic_node(state: CompetitorIntelState):
    print("--- [Critic] Reviewing Draft ---")

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a Quality Assurance AI. Review the draft. If it contains at least one comparison and is formatted well, respond with EXACTLY 'PASS'. Otherwise, give a 1-sentence critique.",
            ),
            ("user", "Draft:\n{draft}\n\nUser Request:\n{user_request}"),
        ]
    )

    response = (prompt | smart_llm).invoke(
        {"draft": state["draft_report"], "user_request": state.get("user_request", "")}
    )

    critique = response.content.strip(" .\"'\n")
    if "PASS" in critique.upper() or state.get("revision_count", 0) >= 2:

        print("--- [Critic] Draft Approved! ---")
        return {"final_report": state["draft_report"]}
    else:
        print(f"--- [Critic] Revision Required: {critique} ---")
        return {"user_request": f"Fix these issues concisely: {critique}"}


def route_critique(state: CompetitorIntelState):
    """Determines if we need to loop back or finish."""
    if state.get("final_report"):
        return END
    return "strategist"


def build_competitor_graph():
    workflow = StateGraph(CompetitorIntelState)

    workflow.add_node("researcher", researcher_node)
    workflow.add_node("internal_analyst", internal_analyst_node)
    workflow.add_node("strategist", strategist_node)
    workflow.add_node("critic", critic_node)

    workflow.add_edge(START, "researcher")
    workflow.add_edge(START, "internal_analyst")
    workflow.add_edge(["researcher", "internal_analyst"], "strategist")
    workflow.add_edge("strategist", "critic")
    workflow.add_conditional_edges(
        "critic", route_critique, {END: END, "strategist": "strategist"}
    )

    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)
