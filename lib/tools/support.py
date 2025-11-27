########## SUPPORT.PY ##########
#### DESC: Python functions that support session and memory for agents.
#### AUTH: Leslie A. McFarlin, from Google 5-Day AI Agents Intensive
#### DATE: 25-Nov-2025

# Imports 
import os
from pathlib import Path
import uuid
import json
from datetime import datetime
from time import perf_counter
import base64
import io
import requests
from IPython.display import Image, display
from PIL import Image as im
import matplotlib.pyplot as plt
from typing import Any, Dict, Optional
from dotenv import load_dotenv
from google.genai import types

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService

# Custom modules
from lib.config import APP_NAME



# ---------- LOGGING FUNCTIONS ----------
# Light logging function
def log_event(event_type: str, **fields) -> None:
    '''
    Event logger that captures timestamp, event type, and key -> value fields.
    
    :param event_type: the type of event
    :type event_type: str
    :param fields: key value associated with the event and its outcome.
    '''
    # timestamp
    ts = datetime.now().isoformat(timespec="seconds")

    # Extra
    extra = " ".join(f"{k}={v}" for k,v in fields.items())

    # Print
    print(f"[{ts}] [{event_type}] {extra}")



# ---------- AGENT TOOL FUNCTIONS ----------
# Extracts the tool result
def extract_tool_result(event, tool_name="build_task_flow"):
    '''
    Extracts a tools results
    
    :param event: the event processed by a tool.
    :param tool_name: the tool processing the event.
    '''                    
    # Content
    content = getattr(event, "content", None)
    if not content or not getattr(content, "parts", None):
        return None
    
    # Iterate parts in content.parts
    for part in content.parts:
        function_response = getattr(part, "function_response", None)
        tool_response = getattr(part, "tool_response", None)

        resp = function_response or tool_response
        if not resp:
            continue

        name = getattr(resp, "name", "")
        if name != tool_name:
            continue

        # Get the actual output
        output = getattr(resp, "output", None)
        if output is None:
            output = getattr(resp, "response", None) or getattr(resp, "result", None)

        # Already a dict
        if isinstance(output, dict):
            return output
        
        # JSON string
        if isinstance(output, str):
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                return None
            
    # Return
    return None



# Save out to Mermaid
def save_mermaid(result: Dict[str, Any], path: str | Path) -> Path:
    '''
    Save the Mermaid diagram from a task_flow result to a .mmd file.
    
    :param result: dict returned by build_task_flow (tool results)
    :type result: Dict[str, Any]
    :param path: path to save .mmd file
    :type path: str | Path
    :return: the path with the saved .mmd file
    :rtype: Path
    '''
    # get the mermaid diagram
    mermaid = result.get("mermaid")
    if not mermaid:
        raise ValueError("No mermaid diagram found in result. There is nothing to save.")
    
    # Get the path
    path = Path(path)
    if path.suffix=="":
        path = path.with_suffix(".mmd")

    # Save out the mmd file.
    path.write_text(mermaid, encoding="utf-8")
    print(f"Mermaid diagram saved to: {path}")

    # Return the saved .mmd file
    return path



# Renders graphs
def render_mermaid_via_mermaid_ink(
        mermaid_str: str, 
        output_path: str | Path,
        title: str | None,
        dpi:int = 300,
        show: bool = True
        ) -> Path:
    '''
    Draws a mermaid chart from a specified string.

    Arguments:
    - mermaid_str: the chart to draw.
    - output_path: Where to save the PNG.
    - title: Optional plot title for the displayed image.
    - dpi: chart resolution. Defaults to 300 dpi.
    - show: Whether to display the image inline (matplotlib).

    Returns:
    - Path to the saved PNG file. 
    '''
    # Encoding from string
    graphbytes = mermaid_str.encode("utf8")
    base64_bytes = base64.urlsafe_b64encode(graphbytes)
    base64_string = base64_bytes.decode("ascii")

    # Builds the image
    img = im.open(io.BytesIO(requests.get('https://mermaid.ink/img/'+base64_string).content))

    output_path = Path(output_path)
    if output_path.suffix=="":
        output_path = output_path.with_suffix(".png")

    # Render
    if show:
        # Displays the image
        plt.imshow(img)
        if title:
            plt.title(title)
        else:
            plt.title("Mermaid Task Flow")
        plt.axis("off")  

    # Save the image
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, format="PNG", dpi=(dpi,dpi))
    print(f"PNG saved to {output_path}")



# Prettified output
def pretty_print_taskflow_result(result: Dict[str, Any]) -> None:
    '''
    Prettified display of build_task_flow.
    - title
    - validation + issues
    - mermaid diagram block
    
    :param result: the output of build_task_flow
    :type result: Dict[str, Any]
    '''
    # pretty print preface
    pretty_print_preface = "[pretty_print_taskflow_result]"

    # No results
    if not result:
        print(f"\n{pretty_print_preface} No result to display")

    # Core
    title = result.get("title", "Untitled Flow")
    validation = result.get("validation", {})
    mermaid = result.get("mermaid", "")

    # Display
    print("\n========== TASK FLOW ==========")
    print(f"Title: {title}\n")

    print("Validation:")
    valid = validation.get("valid")
    print(f"    Valid: {valid}")

    issues = validation.get("issues", [])
    if issues:
        # Iterate
        for issue in issues:
            msg = issues.get("message") or str(issue)
            print(f"    - {msg}")

    else:
        if valid is True:
            print("     No issues found.")
        else:
            print("     No issues listed, but validity is unclear.")

    if mermaid:
        print("\nMermaid diagram:\n")
        print(mermaid)
        print("\nCopy this into a Mermaid preview to see the diagram.")
        # Call save_mermaid
        title_parsed = title.split()
        file_name = '_'.join([word for word in title_parsed])
        save_mermaid(result, f"{file_name}.mmd")
        # Render via render_mermaid_via_mermaid_ink
        render_mermaid_via_mermaid_ink(
            mermaid_str=mermaid,
            output_path=f"{file_name}.png",
            title=title,
            dpi=300,
            show=True
        )
    else:
        print("\nNo Mermaid diagram found in result.")



# Run queries in a session - based on Google 5-Day AI Agents Intensive
async def run_session(
    runner_instance: Runner,
    user_queries: list[str] | str,
    memory_service: InMemoryMemoryService,
    session_service: InMemorySessionService,
    user_id: str,
    session_id: str
) -> None:
    """
    Helper function to run queries in a session and display responses.
    """

    print(f"\n##### Session: {session_id}")

    # Creates the new session, will move on if it exists already
    try:
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )
        # Confirm session has been created
        print(f"Session created for: {APP_NAME}, {user_id}, {session_id}")
    except Exception:
        # Session already exists - confirm and go forward
        print(f"Session already exists for: {APP_NAME}, {user_id}, {session_id}")
        pass

    # Normalize to list
    if isinstance(user_queries, str):
        user_queries = [user_queries]

    # Process each query
    for query in user_queries:
        print(f"\nUser > {query}")
        # Log the event timestamp
        log_event(
            "query_start",
            user_id=user_id,
            session_id=session_id,
            query=query
        )

        query_content = types.Content(
            role="user",
            parts=[types.Part(text=query)],
        )

        # Track timing
        start_time = perf_counter()
        tool_called = False
        last_valid: bool | None = None

        # IMPORTANT: use run_async here, not run
        events = runner_instance.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=query_content,
        )

        # Iterate events
        async for event in events:
            # Tool results
            responses = event.get_function_responses()
            if responses:
                for resp in responses:
                     if resp.name == "build_task_flow":
                        tool_called = True
                        result_dict = resp.response

                        # Validation flag for logging
                        validation = result_dict.get("wavlidation", {})
                        last_valid = validation.get("valid")

                        # Task flow result
                        pretty_print_taskflow_result(result_dict)

            # The final LLM Message
            if event.is_final_response() and event.content and event.content.parts:
                # Pulls out the model-facing text
                first_part = event.content.parts[0]
                text = getattr(first_part, "text", None)
                if text and text != "None":
                    print(f"Model > {text}")

            # Query is finished - capture timing and validation
            time_elapsed = perf_counter() - start_time
            log_event(
                "query_complete",
                user_id=user_id,
                session_id=session_id,
                query=query,
                seconds=round(time_elapsed, 3),
                tool_called=tool_called,
                valid=last_valid,
        )
