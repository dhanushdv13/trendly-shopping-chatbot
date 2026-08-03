import os
from typing import Literal

from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

# Import our tools and state
from app.tools import (
    get_order as _get_order,
    search_policy as _search_policy,
    check_return_eligibility as _check_return_eligibility,
    create_return as _create_return,
    create_exchange as _create_exchange,
    escalate_to_human as _escalate_to_human,
)
from app.state import AgentState
from app.prompts import SYSTEM_PROMPT_V1

# We use Groq as specified in requirements.txt
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# Wrap our pure python tools in LangChain's @tool decorator
@tool
def get_order(order_id: str):
    """Retrieve order details for a given order ID (e.g., 'ORD101')."""
    return _get_order(order_id)

@tool
def search_policy(query: str):
    """Search the Trendly store policy for information relevant to the query."""
    return _search_policy(query)

@tool
def check_return_eligibility(order_id: str):
    """Check if a given order is eligible for a return based on the store's return policy."""
    return _check_return_eligibility(order_id)

@tool
def create_return(order_id: str):
    """Initiate a return for a given order."""
    return _create_return(order_id)

@tool
def create_exchange(order_id: str, new_item: str):
    """Initiate an exchange for a given order to get a new item."""
    return _create_exchange(order_id, new_item)

@tool
def escalate_to_human(order_id: str, issue: str, order_status: str, actions_taken: str, reason: str):
    """Escalate the customer's issue to a human support agent."""
    # Note: Using str for optional arguments in @tool since some LLMs handle Optional poorly
    return _escalate_to_human(order_id, issue, order_status, actions_taken, reason)

tools = [
    get_order,
    search_policy,
    check_return_eligibility,
    create_return,
    create_exchange,
    escalate_to_human
]

# Initialize LLM
llm = ChatGroq(model="llama3-8b-8192", temperature=0)
llm_with_tools = llm.bind_tools(tools)

# Define the graph nodes
def call_model(state: AgentState):
    messages = state["messages"]
    
    # If the first message is not our system prompt, we prepend it
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT_V1)] + messages
        
    response = llm_with_tools.invoke(messages)
    
    # Extract order_id if present in tool calls, just for state tracking
    order_id = state.get("order_id")
    escalated = state.get("escalated", False)
    
    if response.tool_calls:
        for t in response.tool_calls:
            if "order_id" in t["args"] and t["args"]["order_id"]:
                order_id = t["args"]["order_id"]
            if t["name"] == "escalate_to_human":
                escalated = True
                
    return {"messages": [response], "order_id": order_id, "escalated": escalated}

# Define the routing logic
def should_continue(state: AgentState) -> Literal["tools", END]:
    messages = state["messages"]
    last_message = messages[-1]
    
    if last_message.tool_calls:
        return "tools"
    return END

# Build the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))

# Add edges
workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
)
workflow.add_edge("tools", "agent")

# Compile with memory
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

if __name__ == "__main__":
    # Ensure you have GROQ_API_KEY set in your environment
    import uuid
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    print("--- Test Graph ---")
    inputs = {"messages": [("user", "Check order ORD101")]}
    
    try:
        for output in app.stream(inputs, config, stream_mode="values"):
            message = output["messages"][-1]
            message.pretty_print()
            
        print("\n--- Test Memory (Multi-turn) ---")
        inputs2 = {"messages": [("user", "Can I return it?")]}
        for output in app.stream(inputs2, config, stream_mode="values"):
            message = output["messages"][-1]
            if message.type != "human": # Just printing the bot's messages
                message.pretty_print()
                
    except Exception as e:
        print(f"Error during graph execution (check API key): {e}")
