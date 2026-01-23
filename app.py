import streamlit as st
import requests
from llama_cpp import Llama
from langgraph.graph import StateGraph, END
from typing import TypedDict

# --- CONFIGURATION ---
MODEL_PATH = "models/qwen3b.gguf"
TOOL_URL = "http://localhost:8000"

# Load AI (Cached)
@st.cache_resource
def load_llm():
    return Llama(
        model_path=MODEL_PATH,
        n_ctx=2048,
        n_gpu_layers=20, # Offload to RTX 3050
        verbose=False
    )

llm = load_llm()

# --- AGENT STATE ---
class AgentState(TypedDict):
    question: str
    context: str
    tool_out: str
    final_ans: str

# --- NODES (LOGIC) ---

def retrieve(state: AgentState):
    """Call Server to search PDFs"""
    try:
        res = requests.post(f"{TOOL_URL}/search", json={"query": state["question"]})
        data = res.json()
        if not data["results"]:
            return {"context": "MISSING"}
        return {"context": "\n".join(data["results"])}
    except:
        return {"context": "Error connecting to server"}

def reason(state: AgentState):
    """Check if math is needed (Bonus Logic)"""
    q = state["question"].lower()
    if "calculate" in q or "how much" in q:
        # Simple extraction for demo: "5g for 2 acres"
        import re
        nums = re.findall(r"\d+", q)
        if len(nums) >= 2: # Found dose and area
            return {"tool_out": f"CALC:{nums[0]},{nums[1]}"}
    return {"tool_out": "NONE"}

def execute_tool(state: AgentState):
    """Call Server to Calculate"""
    if state["tool_out"].startswith("CALC"):
        dose, area = state["tool_out"].replace("CALC:", "").split(",")
        res = requests.post(f"{TOOL_URL}/calculate", json={"dose": float(dose), "area": float(area)})
        return {"tool_out": res.json()["msg"]}
    return {"tool_out": "No calculation needed."}

def generate(state: AgentState):
    """Final Answer"""
    if state["context"] == "MISSING":
        return {"final_ans": "I don't know based on the provided documents."} # Exact Phrase Rule

    prompt = f"""<|im_start|>system
You are an expert. Answer using ONLY the context below. 
If context is missing, say 'I don't know based on the provided documents.'
CONTEXT: {state['context']}
TOOL RESULT: {state['tool_out']}
<|im_end|>
<|im_start|>user
{state['question']}
<|im_end|>
<|im_start|>assistant"""
    
    out = llm(prompt, max_tokens=200, stop=["<|im_end|>"])
    return {"final_ans": out["choices"][0]["text"]}

# --- GRAPH ---
workflow = StateGraph(AgentState)
workflow.add_node("retrieve", retrieve)
workflow.add_node("reason", reason)
workflow.add_node("tool", execute_tool)
workflow.add_node("generate", generate)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "reason")
workflow.add_edge("reason", "tool")
workflow.add_edge("tool", "generate")
workflow.add_edge("generate", END)
app = workflow.compile()

# --- UI ---
st.title("🌾 Agri-Bot (RTX 3050 Edition)")
q = st.chat_input("Ask a question...")
if q:
    st.chat_message("user").write(q)
    res = app.invoke({"question": q, "context": "", "tool_out": "", "final_ans": ""})
    st.chat_message("assistant").write(res["final_ans"])
    with st.expander("Debug Agent Logic"): # Transparency Bonus
        st.write(f"Retrieved: {res['context'][:100]}...")
        st.write(f"Tool: {res['tool_out']}")