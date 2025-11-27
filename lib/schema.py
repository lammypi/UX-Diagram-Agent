########## SCHEMA.PY ##########
#### DESC: Defines the components of the diagrams.
#### AUTH: Leslie A. McFarlin, Principal UX Architect
#### DATE: 24-Nov-2025

# Imports
from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, List, Literal, TypedDict, Optional

# ---------- COMPONENT DEFINITIONS ----------
### Core Components
#   - NodeType: Specifies the types of nodes in a chart
#               that will be derived from Node class.
#               - Class with the following values:
#                   1. start- starting point of a diagram.
#                   2. process- node that is part of a process.
#                   3. decision- node marking a decision point.
#                   4. end- ending point of a diagram.
#   - ActorType: Speficies who is performing the action 
#                at a node.
#                - Defined as a literal with the following values:
#                   1. user- the end user of a process.
#                   2. system- the system a user is interacting with. 

# NodeType - an Enum, fixed set of specified constants.
# Controls the vocabulary of allowed node types
# Does not support typos (e.g., "start" and never "staart")
class NodeType(str, Enum):
    START = "start"
    PROCESS = "process"
    DECISION = "decision"
    END = "end"

# ActorType
ActorType = Literal["user", "system"]



# ---------- NODE ----------
### Node is a class meant to hold data about a node object.
# Node data is sent to a dictionary that will be used in a
# task flow.
@dataclass
class Node:
    id: str # Unique identifier per node.
    label: str # Display label on the node.
    actor: ActorType # who is acting at this node.
    type: NodeType # START / PROCESS / DECISION / END

    # Send node details to a dictionary
    def to_dict(self) -> Dict[str,Any]:
        ''' Creates a dictionary storing node data. '''
        # Converts to a dictionary
        d = asdict(self)
        # Store the enum as a value
        d["type"] = self.type.value
        # Return
        return d
    


# ---------- EDGE ----------
### Edge is a class meant to hold data about the connection between nodes.
@dataclass
class Edge:
    source: str # id of a source node
    target: str # id of a target node
    condition: Optional[str] = None # If set is a conditional connection

    # Send edge details to a dictionary
    def to_dict(self) -> Dict[str,Any]:
        ''' Creates a dictionary of edge data '''
        # return a dictionary of Edge details
        return {
            "from": self.source,
            "to": self.target,
            "condition": self.condition
        }
    


# ---------- TASK FLOW ----------
### TaskFlow is a class holding data about nodes and edges.
@dataclass
class TaskFlow:
    title: str # Display name of the flow
    actors: List[ActorType] # collection of system and user
    nodes: List[Node] # collection of nodes
    edges: List[Edge] # collection of (source, target, condition)

    # Send task flow details to a dictionary
    def to_dict(self) -> Dict[str, Any]:
        ''' Creates a dictionary of task flow data. '''
        # Return a dictionary
        return {
            "title": self.title,
            "actors": self.actors,
            "nodes": [n.to_dict() for n in self.nodes], # List of nodes with their details as a dictionary
            "edges": [e.to_dict() for e in self.edges]
        }
    
    # Construct from a dict - read and access TaskFlow class variables
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskFlow":
        # Construct nodes
        nodes = [
            Node(
                id=n["id"],
                label=n["label"],
                actor=n["actor"],
                type=NodeType(n["type"]),
            )
            for n in data.get("nodes", [])
        ]

        # Construct edges
        edges = [
            Edge(
                source=e["from"],
                target=e["to"],
                condition=e.get("condition")
            )
            for e in data.get("edges", [])
        ]

        # Return
        return cls(
            title=data.get("title", "Untitled Flow"),
            actors=data.get("actors", ["user", "system"]),
            nodes=nodes,
            edges=edges,
        )