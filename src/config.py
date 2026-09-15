from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Repo root, resolved from this file — so data and static paths work no matter
# which directory the process was started from.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv() # reads .env → environment variables. Runs once, at import.

def create_llm(model:str = "gpt-4o-mini"):
    return ChatOpenAI(model=model, temperature=0)

# temperature=0 makes answers near-deterministic — easier to debug while learning.
# This function is the only place in the whole project that knows which provider you use. 
# In M5, adding Claude support means editing this one function — nothing else changes. 
# That's the same trick the original's create_llm plays with three Azure providers across 14 agents.

