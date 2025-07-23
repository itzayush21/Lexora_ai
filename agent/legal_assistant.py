import os
from typing import Literal
from dotenv import load_dotenv
from langgraph.graph import StateGraph, MessagesState , END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, SystemMessage , ToolMessage
from langchain_core.tools import tool
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch


# === Load Keys ===
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
os.environ["HUGGINGFACEHUB_API_TOKEN"] = hf_token

# === Shared Components ===
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)
embedding_model = GPT4AllEmbeddings()

# === TOOL 1: Constitution RAG Tool ===
@tool
def legal_constitution_rag_tool(query: str) -> str:
    """Answer using the Constitution of India (local PDF)."""
    vectorstore = Chroma(
        persist_directory="data/vectorstores/constitution",
        embedding_function=embedding_model
    )
    retriever = vectorstore.as_retriever()
    results = retriever.invoke(query)

    # Join top chunks
    context = "\n\n".join([doc.page_content for doc in results[:3]])

    #print(f"[TOOL CALL] legal_constitution_rag_tool(query='{query}') with context: {context}...")
    return context

# === TOOL 2: Live Search Tool ===
def legal_web_search_tool(query: str) -> str:
    """Answer using live web search for recent news or legal updates."""
    search = TavilySearch(
        max_results=3, include_answer=True, search_depth="advanced", return_direct=True
    )
    return search.invoke(query)

# === LLM and Tools ===
tools = [legal_constitution_rag_tool, legal_web_search_tool]
tool_node = ToolNode(tools)
llm = ChatGroq(model="llama3-8b-8192", temperature=0).bind_tools(tools)


# === State Graph ===
def should_continue(state: MessagesState) -> Literal["tools", END]:
    messages = state['messages']
    last_message = messages[-1]
    # If the LLM makes a tool call, go to the "tools" node
    if last_message.tool_calls:
        return "tools"
    # Otherwise, finish the workflow
    return END


# Function that invokes the model
def call_model(state: MessagesState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}


# === Define the Workflow ===
# Define the workflow with LangGraph
workflow = StateGraph(MessagesState)

# Add nodes to the graph
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)


# Connect nodes
# Initial entry
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue)  # Decision after the "agent" node
  # If tool call is made, go to "tools"
workflow.add_edge("tools", "agent")  # After tools are called, return to "agent" for next response


# === Checkpointing ===
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)

# === System Prompt ===
SYSTEM_PROMPT = SystemMessage(content="""
You are a helpful and knowledgeable legal assistant specializing in Indian law.

Your role is to explain legal topics clearly and accurately, especially related to the Constitution of India.

TOOL USAGE:
- Use the **Constitution tool** for questions about fundamental rights, constitutional articles, duties, or Indian law.
- Use `legal_web_search_tool` ONLY when:
  - The user mentions "recent", "latest", "current", "in news", or "update".
  - The query implies a real-world case, judgment, or government development.
  - The user asks for **real-life examples**, ongoing debates, or enforcement issue
- Treat tools as assistants, not the sole source. Supplement tool outputs with your own legal expertise, but always clearly distinguish between information retrieved from tools and your own inferred or reasoned knowledge.

RESPONSE STRUCTURE:
- Present answers in a clear, structured format with bullet points or numbered lists where helpful.
- Use **simple, non-technical language** unless legal terms are necessary. Always explain legal jargon in plain English.
- Keep responses concise and focused. Prioritize relevance.
- If the information is not found, clearly state that and suggest possible clarifications or follow-ups.

TONE:
- Be neutral, respectful, and professional.
- Avoid assumptions. Base answers only on retrieved information or verifiable legal facts.

END GOAL:
- Always end with a brief summary or conclusion to reinforce understanding.
- The user should leave with clarity, not confusion.
""")


# === Run Query ===

def legal_chat(query: str) -> MessagesState:
    """Run the legal chat workflow with the given query."""
    # Initialize the state with the system prompt and user query
    initial_state = {
        "messages": [SYSTEM_PROMPT, HumanMessage(content=query)],
        "tool_call_count": 0  # Initial tool call count
    }
    
    # Invoke the workflow
    response=app.invoke(initial_state, config={"configurable": {"thread_id": "constitution-thread"}})
    print(f"[RESPONSE] {response}") # Print the last message content
    return response["messages"][-1].content  # Return the last message content as the response