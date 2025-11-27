# UX-Diagram-Agent
Submission for the Google 5-Day AI Agents Intensive.

**Category:** Enterprise Agents

**Summary:** Creates user flows in Mermaid that users can then edit as necessary. The agent will also generate .mmd files and PNG files of the flows it creates. It's the .mmd files that can be edited in greater detail by the user if needed, and then pasted into [Mermaid Live Editor](https://mermaid.live/).

---

## The Pitch

**Problem**: UX designers and researchers often have to manually translate task descriptions into flow diagrams using tools like Mermaid or Miro. As the previous sentence implies, sometimes these tools are used in traditional tool ecosystems. Other times, they are used in AI-supported tool ecosystems (example: Lovable --> Builder.io --> Figma) where it's critical to the efficiency and quality of the project to have at least a loosely defined task flow before using tools. Regardless of the type of tool ecosystem a UXer works within, creating task flows can be tedious, time-consuming, and occasionally inconsistent.

**Solution**: An LLM-powered UX Task Flow Builder that does the steps outlined below.
- Receives a natural language description of a UX task or flow.
- Asks clarifiying questions about the flow if needed.
- Calls a tool to generate a structured graph (nodes for the steps, edges to indicate links between nodes).
- Validates the flow
- Outputs a Mermaid diagram, complete with a .mmd file and rendered PNG.

**Value**: Allows for faster iteration on task flows with better consistency. This has a downstream effect of easier handoffs to other UXers, Product Managers or Owners, and engineering teams. It can also slot into an AI-infused tool workflow by providing better defined design prompts to tools such as Lovable.
- The output of this agent could be extended to integrate with Miro.


## The Implementation   

At a high level this is a single agent architecture supported by a full suite of tools.
- The agent (TaskBuilderAgent) is built with ```LlmAgent``` using Gemini 2.5 Flash Lite.
  - Implemented within lib/agents/taskflow_agent.py
  - Interactive via ux_diagramming_agent.ipynb
  - Session and state management provided via ```InMemorySessionService``` and ```InMemoryMemoryService```, with explicit ```USER_ID``` and ```SESSION_ID``` per session.
  - Observability via ```log_event()``` that captures timing (```perf_counter```) and logs of tools called and status (```tool_called```).
- 3 tools support the agent (found within lib/tools/builder.py):
  1. ```validate_flow()``` - validates the task flow according to a set of rules.
  2. ```flow_to_mermaid()``` - converts a validated task flow to Mermaid's grammar.
  3. ```build_task_flow()``` - tool that renders full results to the user.
- A series of support functions the enable the creation of .mmd files and rendering of task flow PNG files located in lib/tools/support.py:
  1. ```log_event()``` - captures timestamp, event type, and validity status of an event.
  2. ```extract_tool_result()``` - extracts results from the tools supporting the agent (see above).
  3. ```save_mermaid()``` - saves a Mermaid taskflow to a .mmd file.
  4. ```render_mermaid_via_mermaid_ink()``` - draws a Mermaid chart from a parsed string as a PNG, and saves it to a specified location.
  5. ```pretty_print_taskflow_result()``` - displays a human-readable string of LLM Agent output regarding a Mermaid task flow.
  6. ```run_session()``` - passes user query information to the LLM Agent during a session.

It's important to also mention here that the modularity of the agent means it will be easier to extend with additional agents and tools (example: specifying styling based on node type).


### How the Agent Defines Task Flows   

From a non-technical perspective, task flows have the following components which are used as rules for task flow creation with this agent:
- A single ```start``` node
  - Has only one outgoing edge
- One or more ```process``` nodes
  - Has at least one outgoing edge, and one incoming edge
- Zero or more ```decision``` nodes
  - Has at least two outgoing edges, and at least one incoming edge
- At least one ```end``` node
  - Has at least one incoming edge and no outgoing edges.

Nodes, edges, and taskflows are defined within lib/schema.py
- Classes for ```NodeType```, ```Node```, ```Edge```, and ```TaskFlow```.


## Instructions

This implementation works best running locally in a Python 3.12 environment. 

1. Clone the repo and enter the project directory.
   ```
   git clone <UX-Diagram-Agent>.git
   cd <UX-Diagram-Agent>
   ```
   
2. Create a virtual environment- ```venv``` or Conda will work, but the code below is only for ```venv```.
   ```
   python -m venv .venv

   # On Windows use this line
   .venv\Scripts\activate

   # On Mac use this line
   source .venv/bin/activate
   ```
   
3. Install dependencies via the provided ```requirements.txt```
   ```
   pip install -r requirements.txt
   ```
   
4. Configure your Google API key- this project uses Gemini via the Google AI APIs and expects an environment variable named GOOGLE_API_KEY. You can set it via a ```.env``` file like below:
```
GOOGLE_API_KEY = "YOUR_API_KEY_HERE"
```

You can also export it directly in your shell:
```
# On Windows
set GOOGLE_API_KEY=YOUR_API_KEY_HERE

# On Mac
export GOOGLE_API_KEY=YOUR_API_KEY_HERE
```

5. Verify the file structure- the minimal file structure required to run this project appears below.
```
(root)
├── ux_diagramming_agent.ipynb
├── requirements.txt
├── lib/
    ├── agent_diagram.py        # (This generates the architecture image in the notebook)
    ├── config.py
    ├── schema.py
    ├── agents/
    │   └── taskflow_agent.py
    └── tools/
        ├── builder.py
        └── support.py
```
   
6. Run the notebook- you may need to initialize Jupyter Notebook or Lab to run the notebook in the project root directory.
```
# If you need to, select one of the options for starting jupyter
jupyter notebook

# Lab
jupyter lab
```

Once that is activated, you can open ```ux_diagramming_agent.ipynb``` and run the cells in order. Keep in mind if you want to try new prompts not shown in the notebook:

1. The very first time you run the Agent during the session, use ```await run_session()``` with the details specified in the function signature.
2. After the first call in a session, use ```await chat()```. You only need to pass it a string.

.mmd files and PNG files will be saved to directories that you can specify. If you don't specify, these files will be save in the project root level.

A successful run should generate a task flow diagram as Mermaid text and a PNG image, along with details on where file locations.

---
#### License / Use

Copyright © 2025, Leslie McFarlin.  
All rights reserved.

This repository is provided solely for educational and portfolio review purposes (e.g., course grading, personal demonstration). No permission is granted to use, copy, modify, or distribute this code or content without the explicit written consent of the author. 



