from abc import ABC, abstractmethod
from dotenv import load_dotenv

# Load .env into environment
load_dotenv()


class LLMAdapter(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def get_params(self) -> dict:
        """Returns the dictionary of parameters to pass to guard()."""
        pass
