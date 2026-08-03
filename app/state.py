from typing import TypedDict, Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    Represents the state of our LangGraph agent.
    
    Attributes:
        messages: The conversation history, managed by add_messages to append new ones.
        order_id: The ID of the order currently in context, if any.
        intent: The customer's identified intent.
        escalated: A flag to indicate whether this conversation has been escalated to a human.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    order_id: Optional[str]
    intent: Optional[str]
    escalated: bool
