from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from app.agent import app as agent_app

app = FastAPI(title="Trendly Support Agent API")

# Add CORS middleware to allow communication from any frontend (local or deployed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint required for deployment."""
    return {"status": "healthy"}

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str
    escalated: bool

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        config = {"configurable": {"thread_id": request.session_id}}
        inputs = {"messages": [("user", request.message)]}
        
        # We will stream the graph but only collect the final message
        final_message = None
        escalated = False
        
        for output in agent_app.stream(inputs, config, stream_mode="values"):
            # output["messages"] contains the full conversation state
            messages = output.get("messages", [])
            if messages:
                last_msg = messages[-1]
                # Keep track if the agent sent a message
                if last_msg.type == "ai":
                    final_message = last_msg
            
            if output.get("escalated"):
                escalated = True
                
        if not final_message:
            return ChatResponse(reply="I'm sorry, I couldn't process that.", escalated=escalated)
            
        reply_text = final_message.content if isinstance(final_message.content, str) else str(final_message.content)
        
        # Check escalated flag from the current state (as returned by the agent)
        state = agent_app.get_state(config).values
        final_escalated = state.get("escalated", escalated)
            
        return ChatResponse(
            reply=reply_text,
            escalated=final_escalated
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
