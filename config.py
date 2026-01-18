import os
from dotenv import load_dotenv
from model_adapters.gemini_adapter import GeminiAdapter
from model_adapters.mock_adapter import MockAdapter
from model_adapters.gpt_adapter import GPTAdapter
from model_adapters.groq_adapter import GroqAdapter

# Load environment variables
load_dotenv()

# --- FRAMEWORK CONFIGURATION ---
# These settings control the validation framework behavior
# Domain-specific settings (task, items, schema) are in examples/domains/

# === CONSENSUS CONFIGURATION ===
# Number of API calls per item for consensus
CONSENSUS_ITERATIONS = 5
assert CONSENSUS_ITERATIONS > 0, "CONSENSUS_ITERATIONS must be positive"

# Consensus threshold as a ratio (0.0 to 1.0)
# Automatically converted to absolute number in the verifier
# e.g., 0.6 with 5 iterations = ceil(5 * 0.6) = 3 votes required
CONSENSUS_THRESHOLD_RATIO = 0.6
assert 0.0 <= CONSENSUS_THRESHOLD_RATIO <= 1.0, (
    "CONSENSUS_THRESHOLD_RATIO must be between 0.0 and 1.0"
)

# === ADAPTER CONFIGURATION ===
# Default adapter to use: "groq", "gpt", "gemini", or "mock"
DEFAULT_ADAPTER_TYPE = "groq"

# === DATABASE CONFIGURATION ===
# Directory for storing validation databases
DATA_DIR = "data"

# Default database filename (used if domain doesn't specify one)
DEFAULT_DB_NAME = "validation_logs.db"

# Full default database path
DATABASE_PATH = os.path.join(DATA_DIR, DEFAULT_DB_NAME)

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)


# --- ADAPTER FACTORY ---


def get_selected_adapter(adapter_type: str | None = None):
    """Returns the adapter instance based on type."""
    adapter_type = adapter_type or DEFAULT_ADAPTER_TYPE

    adapters = {
        "groq": GroqAdapter,
        "gpt": GPTAdapter,
        "gemini": GeminiAdapter,
        "mock": MockAdapter,
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


def get_db_path(domain_config):
    """
    Get database path for a domain config.
    Uses domain's DATABASE_PATH if specified, otherwise uses default.
    Ensures the path is in the data directory.
    """
    if hasattr(domain_config, "DATABASE_PATH"):
        db_path = domain_config.DATABASE_PATH
    else:
        db_path = DATABASE_PATH

    # Ensure it's in the data directory
    if not db_path.startswith(DATA_DIR):
        # Extract just the filename and put it in data dir
        db_filename = os.path.basename(db_path)
        db_path = os.path.join(DATA_DIR, db_filename)

    return db_path
