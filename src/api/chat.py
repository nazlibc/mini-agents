import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.agents.registry import get_agent
from src.agents.router import classify_agent

router=APIRouter()

class ChatRequest(BaseModel):
    message: str
    agent: str = "AUTO"

def _sse(event: str, data) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"

@router.post("/chat/stream")
def chat_stream(req: ChatRequest):
    def gen():
        try:
            agent_id = classify_agent(req.message) if req.agent == "AUTO" else req.agent
            yield _sse("agent", {"agent": agent_id}) # tell the client which agent is being used
            for kind, data in get_agent(agent_id).stream_chat(req.message):
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


