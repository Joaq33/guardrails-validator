import os
from dotenv import load_dotenv
from adapters.gemini_adapter import GeminiAdapter
from adapters.mock_adapter import MockAdapter
from adapters.gpt_adapter import GPTAdapter
from adapters.groq_adapter import GroqAdapter
from models import HeroCapabilities  # Import your schema

# --- QUICK SETUP ---

# === VALIDATION TASK CONFIGURATION ===
# Description of what you're validating (used in prompts)
VALIDATION_TASK = "superhero capabilities"

# Items to validate (can be any list of strings)
ITEMS_TO_VALIDATE = ["Thor", "Iron Man", "Captain America", "Wolverine","Superman", "Aquaman", "Spiderman", "Black Panther", "Hulk", "Black Widow"]

# The Pydantic model schema to use for validation
# Change this to use a different schema for different domains
VALIDATION_SCHEMA = HeroCapabilities

# === CONSENSUS CONFIGURATION ===
# Number of API calls per item for consensus
CONSENSUS_ITERATIONS = 5

# Consensus threshold as a ratio (0.0 to 1.0)
# This will be automatically converted to an absolute number in the verifier
# e.g., 0.6 with 5 iterations = ceil(5 * 0.6) = 3 votes required
CONSENSUS_THRESHOLD_RATIO = 0.6

# === ADAPTER CONFIGURATION ===
# Default adapter to use: "groq", "gpt", "gemini", or "mock"
DEFAULT_ADAPTER_TYPE = "groq"

# === DATABASE CONFIGURATION ===
# Path to SQLite database for logging validation responses
DATABASE_PATH = "validation_logs.db"

# --------------------

# Load environment variables
load_dotenv()

def get_selected_adapter(adapter_type: str = None):
    """Returns the adapter instance based on type."""
    adapter_type = adapter_type or DEFAULT_ADAPTER_TYPE
    
    adapters = {
        "groq": GroqAdapter,
        "gpt": GPTAdapter,
        "gemini": GeminiAdapter,
        "mock": MockAdapter
    }
    
    adapter_class = adapters.get(adapter_type.lower())
    if not adapter_class:
        raise ValueError(f"Unknown adapter type: {adapter_type}")

    try:
        return adapter_class()
    except Exception as e:
        print(f"Initialization Error for {adapter_type}: {e}")
        print("Falling back to MockAdapter for demonstration.")
        return MockAdapter()
