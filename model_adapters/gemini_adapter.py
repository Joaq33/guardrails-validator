import os
from llm_adapters import LLMAdapter

class GeminiAdapter(LLMAdapter):
    def __init__(self):
        self.api_key = os.getenv("GENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("Set the GENAI_API_KEY environment variable before running.")
        
        # LiteLLM/Guardrails expects GEMINI_API_KEY but our env has GENAI_API_KEY
        # Let's set the expected one.
        os.environ["GEMINI_API_KEY"] = self.api_key

    def get_params(self) -> dict:
        return {
            "model": "gemini/gemini-2.5-flash-lite", 
        }
