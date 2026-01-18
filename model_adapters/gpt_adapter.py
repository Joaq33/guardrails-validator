import os
from llm_adapters import LLMAdapter


class GPTAdapter(LLMAdapter):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "Set the OPENAI_API_KEY environment variable before running."
            )

    def get_params(self) -> dict:
        return {"model": "gpt-4o", "api_key": self.api_key}
