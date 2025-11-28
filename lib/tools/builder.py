########## BUILDER.PY ##########
#### DESC: Tools for building flows in Mermaid. Used by the Builder agent.
#### AUTH: Leslie A. McFarlin, Principal UX Architect
#### DATE: 24-Nov-2025

# Imports
from typing import List, Dict, Any



# ---------- FUNCTIONS ----------
# Validates a flow meets all of the rules before being 
# rendered in Mermaid.
def validate_flow(flow: Dict[str, Any]) -> Dict[str, Any]:
    '''
    Returns a dictionary detailing the validity of a flow
    and what issues exist if any.
    1. Identifies start, end, and decision nodes.
       - Only one start node.
       - At least one end node.
       - Decision nodes have at least two connections.
    2. Create an adjacency map to match source and target nodes.
    3. Check edges
    4. Check decision nodes

    Arguments:
    - flow: a dictionary of flow components.

    Returns:
    - a dictionary of flow validity details.
    '''
    # Issues holding list
    issues: List[Dict[str, Any]] = []

    ### Type + structure checks
    if not isinstance(flow, dict):
        issues.append({
            "type": "invalid_type",
            "message": f"Flow must be a dict with 'nodes' and 'edges', but got {type(flow).__name__}: {flow!r}"
            }
        )
        # Return
        return {"valid": False, "issues": issues}
    
    # Raw details
    nodes_raw = flow.get("nodes")
    edges_raw = flow.get("edges")

    if not isinstance(nodes_raw, list) or not isinstance(edges_raw, list):
        issues.append({
            "type": "invalid_structure",
            "message": "Flow must have 'nodes' and 'edges' as lists. "
        })
        # Return
        return {"valid": False, "issues": issues}

    # STEP 1A : Start/end/decision nodes
    nodes = {n["id"]: n for n in nodes_raw if isinstance(n, dict) and "id" in n}
    edges = [e for e in edges_raw if isinstance(e, dict)]

    # Note if something important was lost
    if len(nodes) == 0:
        issues.append({
            "type": "no_nodes",
            "message": "Flow has no valid node definitions."
        })

    # NODE ROLES
    start_nodes = [n for n in nodes.values() if n.get("type") == "start"]
    end_nodes = [n for n in nodes.values() if n.get("type") == "end"]
    decision_nodes = [n for n in nodes.values() if n.get("type") == "decision"]

    # STEP 1B: Start / end checks
    # Must be 1 start node.
    if len(start_nodes) != 1:
        issues.append(
            {
                "type": "start_node_count",
                "message": f"Flow should have exactly 1 start node, found {len(start_nodes)}."
            }
        )

    # Must be at least 1 end node.
    if len(end_nodes) == 0:
        issues.append(
            {
                "type": "end_node_count",
                "message": "Flow should have at least 1 end node, found 0."
            }
        )

    # STEP 2: BUILD AN ADJACENCY MATRIX
    incoming = {node_id: [] for node_id in nodes}
    outgoing = {node_id: [] for node_id in nodes}

    for e in edges:
        src = e.get("from")
        tgt = e.get("to")

        if src not in nodes:
            issues.append(
                {
                    "type": "edge_source_missing",
                    "message": f"Edge has source '{src}' which is not a node id."
                }
            )

        if tgt not in nodes:
            issues.append(
                {
                    "type": "edge_target_missing",
                    "message": f"Edge has target '{tgt}' which is not a node id."
                }
            )

        if src in outgoing:
            outgoing[src].append(e)
        if tgt in incoming:
            incoming[tgt].append(e)

    # STEP 3: CHECK EDGES
    for node_id, node in nodes.items():
        if node.get("type") != "start" and len(incoming[node_id]) == 0:
            issues.append(
                {
                    "type": "no_incoming_edge",
                    "message": f"Node '{node_id}' has no incoming edges and is not the start node."
                }
            )
        # Non-end nodes have at least one outgoing edge
        if node.get("type") != "end" and len(outgoing[node_id]) == 0:
            issues.append(
                {
                    "type": "no_outgoing_edge",
                    "message": f"Node '{node_id}' has no outgoing edges and is not an end node."
                }
            )

    # STEP 4: CHECK DECISION NODES
    for node in decision_nodes:
        node_id = node["id"]
        outs = outgoing.get(node["id"], [])
        # At least 2 outgoing edges
        if len(outs) < 2:
            issues.append(
                {
                    "type": "decision_branch_count",
                    "message": f"Decision node '{node['id']}' should have at least 2 outgoing edges."
                }
            )

        # Every outgoing edge from a decision node must have a condition.
        for e in outs:
            cond = (e.get("condition") or "").strip()
            if not cond:
                issues.append(
                {
                    "type": "missing_condition",
                    "message": f"Decision edge from '{node['id']}' to '{e.get('to')}' should have a non-empty condition."
                }
            )
    
    # Return 
    return {
        "valid": len(issues) == 0,
        "issues": issues
    }



# ---------- MERMAID RENDERING ----------
# Sending flow to Mermaid
def flow_to_mermaid(flow: Dict[str, Any]) -> Dict[str, str]:
    '''
    Converts the JSON of a TaskFlow to a dictionary.

    Arguments:
    - flow: dictionary of task flow details.

    Returns:
    - a dictionary of task flow details.
    '''
    # Create a minimal diagram if shape is wrong
    if not isinstance(flow, dict):
        return {
            "title": "Invalid Flow",
            "mermaid": "flowchart TD\n ERR[Invalid flow: not a dict]\n"
        }

    # Get nodes and edges
    nodes = flow.get("nodes", [])
    edges = flow.get("edges", [])

    if not isinstance(nodes, list) or not isinstance(edges, list):
        return {
            "title": flow.get("title", "Invalid Flow"),
            "mermaid": "flowchart TD\n ERR[Invalid flow: nodes/edges not lists]\n"
        }

    # Mapping nodes and ID collection
    node_lookup = {n['id']: n for n in nodes if isinstance(n, dict) and "id" in n}
    node_ids = list(node_lookup.keys())

    lines: List[str] = ["flowchart TD"]

    def format_node(node: Dict[str, Any]) -> str:
        label = (node.get("label") or "").replace('"', '\\"')
        node_id = node['id']
        node_type = node.get("type")

        if node_type in ("start", "end"):
            return f'{node_id}([{label}])'
        elif node_type == "decision":
            return f'{node_id}{{{label}}}'
        else:
            return f'{node_id}[{label}]'

    # Full node specification   
    for node_id in node_ids:
        node = node_lookup[node_id]
        lines.append(f" {format_node(node)}")
    
    # Full edge specification
    for e in edges:
        if not isinstance(e, dict):
            continue
        # Source, target, conditions
        src = e.get("from")
        tgt = e.get("to")
        cond = (e.get("condition") or "").strip()

        if not src or tgt:
            # this is a malformed edge, so move on from it
            continue

        if cond:
            cond_clean = cond.replace('"', '\\"')
            lines.append(f'     {src} -->|{cond_clean}| {tgt}')
        else:
            lines.append(f"     {src} --> {tgt}")

    # Build the mermaid string
    mermaid = "\n".join(lines)

    # return
    return {
        "title": flow.get("title", "Untitled Flow"),
        "mermaid": mermaid,
    }



# ---------- TOOL ENTRY POINT ----------

# Build the task flow from a dictionary
def build_task_flow(flow: Dict[str, Any]) -> Dict[str, Any]:
    '''
    Tool for generating a package of the assessment + task flow string.

    Arguments:
    - flow: dictionary of paired flow elements.

    Returns:
    - dictionary of a flow with its validity assessment.
    '''
    # Validation
    validation = validate_flow(flow)

    # Invalid produces a safe minimal diagram
    if not validation.get("valid", False):
        title = "Invalid Flow"
        if isinstance(flow, dict):
            title = flow.get("title", title)

        mermaid = "flowchart TD\n ERR[Invalid flow input. See issues list.]\n"

        # Return
        return {
            "validation": validation,
            "mermaid": mermaid,
            "title": title
        }

    # Result
    mermaid_results = flow_to_mermaid(flow)

    # Return
    return {
        "validation": validation,
        "mermaid": mermaid_results["mermaid"],
        "title": mermaid_results["title"]
    }