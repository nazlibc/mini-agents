from dataclasses import dataclass, field

@dataclass
class AgentDefinition:
    agent_id: str
    name: str
    description: str # one line — the router will read this in M2
    system_prompt: str
    tool_names: list[str] = field(default_factory=list)
    model: str = "gpt-4o-mini"


#Notice there is no behaviour here at all: an agent is configuration.

# now hand-write the reAct loop

from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage
from src.config import create_llm
from src.tools import TOOL_REGISTRY, get_tools_by_name

def run_agent(defn:AgentDefinition, user_text:str) -> str:
    tools = get_tools_by_name(defn.tool_names)
    llm_with_tools = create_llm(defn.model).bind_tools(tools)

    messages = [SystemMessage(defn.system_prompt), HumanMessage(user_text)]

    while True:
        reply = llm_with_tools.invoke(messages)
        messages.append(reply)

        if not reply.tool_calls:
            return reply.content

        for call in reply.tool_calls:
            print(f"  -> calling tool {call['name']} with args {call['args']}")
            tool = TOOL_REGISTRY[call['name']]
            tool_result = tool.invoke(call['args'])
            messages.append(ToolMessage(str(tool_result), tool_call_id=call['id']))


# bind_tools(tools) is what sends the function schemas along with every request — that's all “giving the LLM tools” means.
# The conversation accumulates: system → human → AI (tool request) → tool result → AI… The LLM re-reads everything each iteration; that's how it “remembers” the tool output.
# tool_call_id must echo the request's id — it's how the LLM matches results to requests when it made several calls at once.