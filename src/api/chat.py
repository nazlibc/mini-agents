import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.agents.registry import get_agent
from src.agents.router import classify_agent
from langchain_core.messages import HumanMessage, AIMessage

router=APIRouter()

class ChatRequest(BaseModel):
    message: str
    agent: str = "AUTO"
    history: list[dict] = []

def _to_messages(history: list[dict]) -> list:
    out = []
    for m in history:
        if m.get("type") == "human":
            out.append(HumanMessage(content=m.get("content","")))
        elif m.get("type") == "ai":
            out.append(AIMessage(content=m.get("content","")))
    return out
        
def _sse(event: str, data) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"

@router.post("/chat/stream")
def chat_stream(req: ChatRequest):
    def gen():
        try:
            agent_id = classify_agent(req.message) if req.agent == "AUTO" else req.agent
            agent = get_agent(agent_id)  # validates the id before we announce anything
            yield _sse("agent", {"agent": agent_id}) # tell the client which agent is being used
            for kind, data in agent.stream_chat(req.message, _to_messages(req.history)):
                if kind == "tool_call":
                    yield _sse("tool_call", data)
                elif kind == "tool_result":
                    yield _sse("tool_result", {"content": data})
                elif kind == "response":
                    yield _sse("text_delta", {"text": data})
            yield _sse("done", {})
        except Exception as e:
            yield _sse("error", {"message": str(e)})
    return StreamingResponse(gen(), media_type="text/event-stream")


