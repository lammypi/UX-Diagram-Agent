# UX-Diagram-Agent
Submission for the Google 5-Day AI Agents Intensive.

**Category:** Enterprise Agents

**Summary:** Creates user flows in Mermaid that users can then edit as necessary. The agent will also generate .mmd files and PNG files of the flows it generates for the user. It's the .mmd files that can be edited in greater detail by the user.

---

## The Pitch

**Problem**: UX designers and researchers often have to manually translate task descriptions into flow diagrams using tools like Mermaid or Miro. As the previous sentence implies, sometimes these tools are used in traditional tool ecosystems. Other times, they are used in AI-supported tool ecosystems (example: Lovable --> Builder.io --> Figma) where it's critical to the efficiency and quality of the project to have at least a loosely defined task flow. Regardless of the type of tool ecosystem a UXer works within, creating task flows can be tedious, time-consuming, and occasionally inconsistent.

**Solution**: An LLM-powered UX Task Flow Builder that does the steps outlined below.
- Receives a natural language description of a UX task or flow.
- Asks clarifiying questions about the flow if needed.
- Calls a tool to generate a structured graph (nodes for the steps, edges to indicate links between nodes).
- Validates the flow
- Outputs a Mermaid diagram, complete with a .mmd file and rendered PNG.

**Value**: Allows for faster iteration on task flows with better consistency. This has a downstream effect of easier handoffs to other UXers, Product Managers or Owners, and engineering teams. It can also slot into an AI-infused tool workflow by providing better defined design prompts to tools such as Lovable.
- The output of this agent could be extended to integrate with Miro.


## The Implementation   

At a high level this is a single agent architecture supported by full suite of tools.
- The agent is built with LlmAgent using Gemini 2.5 Flash Lite.
  - Implemented within lib/agents/taskflow_agent.py
- 3 tools support the agent (found within lib/tools/builder.py):
  1. ```validate_flow()``` - validates the task flow according to a set of rules.
  2. ```flow_to_mermaid()``` - converts a validated task flow to Mermaid's grammar.
  3. ```build_task_flow()``` - tool that renders full results to the user.
- A series of support functions the enable the creation of .mmd files and rendering of task flow PNG files.
  - Located in lib/tools/support.py 


### How the Agent Defines Task Flows   

From a non-technical perspective, task flows have the following components which are used as rules for task flow creation with this agent:
- A single start node
  - Has only one outgoing edge
- One or more process nodes
  - Has at least one outgoing edge, and one incoming edge
- Zero or more decision nodes
  - Has at least two outgoing edges, and at least one incoming edge
- At least one end node
  - Has at least one incoming edge and no outgoing edges.

Nodes, edges, and taskflows are defined within lib/schema.py

## Instructions

---
#### License / Use

Copyright © 2025, Leslie McFarlin.  
All rights reserved.

This repository is provided solely for educational and portfolio review purposes (e.g., course grading, personal demonstration). No permission is granted to use, copy, modify, or distribute this code or content without the explicit written consent of the author. 



