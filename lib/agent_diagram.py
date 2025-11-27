########## AGENT_DIAGRAM.PY ##########
#### DESC: Draws diagrams related to agent architecture
#### AUTH: Leslie A. McFarlin, Principal UX Architect
#### DATE: 24-Nov-2025

# Imports
import base64
import io
import requests
from IPython.display import Image, display
from PIL import Image as im
from mermaid import Mermaid
import matplotlib.pyplot as plt
import typing



# ---------- AGENT ARCHITECTURE DIAGRAMS ----------
# Diagrams related to agent architecture

### Diagram for overall agent
# 24-11-2025: Two agent structure
# MainAgent serves as the brains and acts as the interface 
# between the user and BuilderAgent.
# BuilderAgent constructs the chart via Mermaid
#full_agent_graph = """
#    graph LR;
#        BuilderAgent --> validate_flow & flow_to_mermaid
#"""

### Tool Diagrams
# 24-11-2025: BuilderAgent uses two tools.
# validate_flow receives JSON for a flow diagram and validates
# it meets structure rules.
# flow_to_mermaid receives JSON for a flow diagram and outputs it
# to a Mermaid chart.
builder_tool_graph = """
    graph TD;
        BuilderAgent --> validate_flow & flow_to_mermaid
        validate_flow --> flow_to_mermaid
        validate_flow --> BuilderAgent
        flow_to_mermaid --> build_task_flow
"""



# ---------- GRAPHING FUNCTIONS ----------
# Functions for drawing graphs using mermaid-js

# Renders graphs
def mm(graph: str, dpi:int = 1200):
    '''
    Draws a mermaid chart from a specified string.

    Arguments:
    - graph: the chart to draw.
    - dpi: chart resolution. Defaults to 1200 dpi.

    Returns:
    - None. 
    '''
    # Encoding from string
    graphbytes = graph.encode("utf8")
    base64_bytes = base64.urlsafe_b64encode(graphbytes)
    base64_string = base64_bytes.decode("ascii")

    # Builds the image
    img = im.open(io.BytesIO(requests.get('https://mermaid.ink/img/'+base64_string).content))

    # Displays the image
    plt.imshow(img)
    plt.title("Agent Architecture Diagram")
    plt.axis("off")

    # Save the image
    plt.savefig("./img/full_agent_diagram.png", dpi=dpi)
    
