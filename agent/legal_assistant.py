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

    print(f"[TOOL CALL] legal_constitution_rag_tool(query='{query}') with context: {context}...")
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
llm = ChatGroq(model="gemma2-9b-it",max_tokens=2048, temperature=0).bind_tools(tools)


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
You are a helpful legal assistant with expertise in the Indian Constitution.

The user will describe a legal situation or concern — your job is to assist them like a thoughtful legal expert.

Start by understanding the situation in simple terms. Based on that:

1. Use the Constitution RAG system to identify any relevant articles, rights, or legal principles.  
   - Don’t just list them — explain briefly what each article means and **how it connects to the user’s issue**.
   - Use clear, non-technical language when possible.

2. If the issue relates to something that might be in the news, courts, or public domain (e.g., police behavior, protests, housing, fundamental rights violations), use **Tavily or a legal web search** to find any **real-life updates**:  
   - These could be news articles, court decisions, or case studies.  
   - Pick 1–2 strong examples, summarize what happened and what law was involved.

In your final response, combine both parts naturally:

- Start with a short summary of the user’s issue  
- Then explain the relevant articles/laws and how they protect or affect the user  
- Then share any current events or real-life cases that are relevant  
- Conclude with what legal options, protections, or awareness the user should consider

Be natural, as if you're speaking to someone unfamiliar with legal jargon — but still accurate and respectful of constitutional law. Structure your response clearly, but don’t sound robotic.

NOTE: YOU SHUOLD ALSO USE YOUR OWN KNOWLEDGE OF THE INDIAN CONSTITUTION AND LEGAL PRINCIPLES TO PROVIDE A THOUGHTFUL, INFORMATIVE RESPONSE.

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