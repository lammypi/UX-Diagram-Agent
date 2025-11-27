########## TASKFLOW_AGENT.PY ##########
#### DESC: Agent dedicated to constructing a flow based on user feedback.
#### AUTH: Leslie A. McFarlin, Principal UX Architect
#### DATE: 24-Nov-2025

# Import - Base imports
import os
import sys
import uuid
from dotenv import load_dotenv
from google.genai import types

# From Google ADK
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.tools import load_memory, FunctionTool
from google.adk.apps import App

# Custom modules
from lib.tools.builder import build_task_flow
from lib.config import APP_NAME, MODEL_NAME, RETRY_CONFIG


# ---------- SYSTEM PROMPT ----------
system_prompt = """
You are a UX task flow designer agent.

Your job is to turn a natural language description of a product task into a structured
task flow in JSON format using this schema:

{
     "title": "string, short human-readable title of the flow",
    "actors": ["User", "System"],
    "nodes": [
        {
        "id": "string, unique identifier like n1, n2, start, end1",
        "label": "string, what happens at this step in clear UX language",
        "actor": "User | System",
        "type": "start | process | decision | end"
        }
    ],
    "edges": [
        {
        "from": "string, id of source node",
        "to": "string, id of target node",
        "condition": "optional string, mainly for decision branches"
        }
    ]
}

CONVERSATION POLICY
- Read the user's request carefully.
- If the request is clearly specified such that nodes for start, major steps, decisions, and 
  outcomes are obvious, you may proceed directly to call the build_task_flow tool.
- Do not call the build_task_flow tool until you have enough information to identify:
  - Start state
  - Main process steps
  - Any decision points or branches
  - End states, including success or failure where relevant
- If the request is vague or underspecified, ask up to 3 clarifiying questions before calling
  any tools.
  - Ask very specific questions that help disambiguate the flow.
    - Example: Do you want a separate forgot password path?
    - Example: Should error states be included?
- After the user answers your clarifiying questions, summarize your understanding of the task flow in 1 - 3 sentences.
- Then call the build_task_flow tool once with a complete, structured description based on the user's answers.
- Finally, present the user:
  - A brief natural-language summary of the flow.
  - The mermaid diagram and validation results produced by the tool.

CONVERSATION EXAMPLE:
User > Build a flow for user login.
Assistant (you) > Before I build the diagram, I have some additional questions.
                > 1. Do you want to include a forgot password path?
                > 2. Should we model what happens after a failed login (e.g., retry vs. lockout)?
User> Yes, include forgot password. For failed login, just show an error and allow for retry.
Assistant (you) > Got it. I'll create a flow with:
                > - Start: user opens login page.
                > - Process: user enters credentials, system validates them
                > - Decision: credentials valid vs. invalid
                > - Outcome 1: login success
                > - Outcome 2: error and retry
                > - Outcome 3: forgot password flow
(Now the assistant calls the build_task_flow tool with this structured description.)

TASK FLOW RULES
- Exactly one node with type "start".
- At least one node with type "end".
- Every node except the start has at least one incoming edge.
- Every non-end node has at least one outgoing edge.
- Every "decision" node has at least two outgoing edges with non-empty "condition".
- Use concise, action-oriented labels.
- Stay at the level of concrete actions and system responses (no journeys, emotions, etc.).

OUTPUT:
- Respond with only a single JSON object that matches the schema above.
- Do not include any explanation or text outside the JSON.
""".strip()



# ---------- MEMORY + SESSION MANAGEMENT ----------
# Memory
memory_service = InMemoryMemoryService()

# Session
session_service = InMemorySessionService()

# Generate random UUIDs for sessions
USER_ID = str(uuid.uuid4())
SESSION_ID = str(uuid.uuid4())

# ---------- LLM AGENT ----------
# Specify tools, create the agent, create the Runner

# build_task_flow
tool_build_task_flow = FunctionTool(func=build_task_flow)

# Build the agent
agent_task_builder = LlmAgent(
    model=Gemini(model=MODEL_NAME, retry_options=RETRY_CONFIG),
    name="TaskBuilderAgent",
    instruction=system_prompt,
    tools=[tool_build_task_flow, load_memory],
    output_key="task_flow_output"
)

# Runner
runner = Runner(
    agent=agent_task_builder,
    app_name=APP_NAME,
    session_service=session_service,
    memory_service=memory_service
)
