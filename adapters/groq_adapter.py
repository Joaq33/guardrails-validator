import os
from openai import OpenAI
from llm_adapters import LLMAdapter

class GroqAdapter(LLMAdapter):
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise RuntimeError("Set the GROQ_API_KEY environment variable before running. Get one for free at https://console.groq.com/keys")

    def get_params(self) -> dict:
        return {
            "model": "openai/llama-3.1-8b-instant",
            # "model": "openai/llama-3.3-70b-versatile",
            "api_key": self.api_key,
            "base_url": "https://api.groq.com/openai/v1",
            "temperature": 0  # Deterministic for factual tasks
        }
