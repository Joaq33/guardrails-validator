from llm_adapters import LLMAdapter

class MockAdapter(LLMAdapter):
    def get_params(self) -> dict:
        # Mock adapter acts differently; main.py handles it specially or we need to support it.
        # But wait, guardrails doesn't support "mock" provider via params natively?
        # Actually, Guardrails has no native "mock" provider that takes specific params like this.
        # However, looking at main.py:
        #     guard_kwargs = adapter.get_params()
        #     res = guard(..., **guard_kwargs)
        #
        # If we return empty dict, guard() uses default model? Or fails?
        # The user's main.py implies MockAdapter works.
        # If MockAdapter was working before, it was a callable.
        # But now we changed main.py to call guard(**params).
        # This breaks MockAdapter if MockAdapter was a local callable!
        #
        # Use Case in main.py:
        # if adapter is MockAdapter, we might need to handle it.
        # But main.py says:
        #     guard_kwargs = adapter.get_params()
        #     res = guard(..., **guard_kwargs)
        #
        # If MockAdapter returns {"llm_api": self_callable}, then guard uses it!
        # Because `guard(llm_api=...)` is valid.
        # So MockAdapter should return `{"llm_api": self}` and implement `__call__`.
        
        return {"llm_api": self}

    def __call__(self, prompt: str = None, messages: list = None, **kwargs) -> str:
        # Simple logic to return valid JSON based on hero name in prompt
        # Extract hero name from prompt if possible
        if "Superman" in prompt:
            return '{"can_fly": true, "has_super_strength": true, "gender": "male"}'
        elif "Wonder Woman" in prompt:
             return '{"can_fly": true, "has_super_strength": true, "gender": "female"}'
        elif "Batman" in prompt:
             return '{"can_fly": false, "has_super_strength": false, "gender": "male"}'
        
        return '{"can_fly": false, "has_super_strength": false, "gender": "unknown"}'
