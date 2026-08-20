from dataclasses import dataclass, field

from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

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

# Rebuild the loop as a graph

class BaseAgent:
    def __init__(self, defn: AgentDefinition):
        self.defn = defn
        tools = get_tools_by_name(defn.tool_names)
        self.llm_with_tools = create_llm(defn.model).bind_tools(tools)
        self.graph = self._build_graph(tools)

    def _build_graph(self, tools):
        def agent_node(state: AgentState):
            msgs = state['messages']
            if not isinstance(msgs[0],SystemMessage):
                msgs = [SystemMessage(self.defn.system_prompt)] + msgs
            reply = self.llm_with_tools.invoke(msgs)
            return {"messages": [reply]}   # partial update — add_messages appends it

        def should_continue(state: AgentState):
            last = state['messages'][-1]
            return "tools" if last.tool_calls else END
            


        workflow = StateGraph(AgentState)

        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", ToolNode(tools))
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges("agent",should_continue,
                                        {"tools": "tools", END: END})
        workflow.add_edge("tools", "agent")
        return workflow.compile()

        # TODO (5 lines):
        # 1. add node "agent"  → agent_node
        # 2. add node "tools"  → ToolNode(tools)
        # 3. set the entry point to "agent"
        # 4. add conditional edges from "agent" via should_continue → {"tools": "tools", END: END}
        # 5. add an edge "tools" → "agent"   (the loop back!)

    def stream_chat(self, user_text: str):
        state = {"messages": [HumanMessage(user_text)]}
        for update in self.graph.stream(state, stream_mode="updates"):
            for node_name, node_out in update.items():
                for msg in node_out["messages"]:
                    if isinstance(msg, ToolMessage):
                        yield ("tool_result", msg.content)
                    elif msg.tool_calls:
                        for call in msg.tool_calls:
                            yield ("tool_call", {"name": call["name"], "args": call["args"]})
                    else:
                        yield ("response", msg.content)
# A generator hands values out one at a time while the work is still running — exactly what a chat UI needs. The caller decides what to do with each tuple; the agent doesn't know or care that M3 will turn them into SSE events.
# This is the simplified twin of the original's astream_chat_with_tools (base.py:243) — theirs is async and adds a ("thinking", ...) event, same idea.
# Check the ToolMessage case first — ToolMessage has no .tool_calls attribute, so the elif order matters.