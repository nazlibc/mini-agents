from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from src.api.chat import router as chat_router

app = FastAPI(title="mini-agents")
app.include_router(chat_router, prefix="/api")
app.mount("/web", StaticFiles(directory="web"), name="web")

@app.get("/")
def index():
    return FileResponse("web/index.html")


# run it from repo root venv active
# uvicorn src.api.main:app --reload --port 8000