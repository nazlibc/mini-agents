from fastapi import FastAPI
from src.api.chat import router as chat_router

app = FastAPI(title="mini-agents")
app.include_router(chat_router, prefix="/api")

# run it from repo root venv active
# uvicorn src.api.main:app --reload --port 8000