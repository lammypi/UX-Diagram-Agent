########## CONFIG.PY ##########
#### DESC: contains configurations for ux-builder-agent.
#### AUTH: Leslie A. McFarlin, Principal UX Architect
#### DATE: 24-Nov-2025



# Imports
import os
from dotenv import load_dotenv
from google.genai import types



# ---------- AGENT CONSTANTS ----------
# Reusable constants in the agent
# Google API Key
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# App name (required for session)
APP_NAME = "UX_TASKFLOW_BUILDER_APP"

# Model name
MODEL_NAME = "gemini-2.5-flash-lite"

# Retry configuration
RETRY_CONFIG = types.HttpRetryOptions(
    attempts=3,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)