import time
from collections import Counter
from typing import Type
from guardrails import Guard
from pydantic import BaseModel

class HeroVerifier:
    def __init__(self, adapter, schema: Type[BaseModel], validation_task: str = "validation"):
        """
        Initialize verifier with an adapter and Pydantic schema.
        
        Args:
            adapter: LLM adapter instance
            schema: Pydantic model class to validate against
            validation_task: Description of what's being validated (e.g., "superhero capabilities")
        """
        self.adapter = adapter
        self.schema = schema
        self.validation_task = validation_task
        self.guard = Guard.for_pydantic(output_class=schema)

    def verify(self, item_name: str) -> dict:
        """Single check verifier (legacy)."""
        return self._call_guard(item_name)

    def _generate_prompt(self, item_name: str) -> str:
        """Generate prompt dynamically based on schema."""
        # Get field information from schema
        fields_desc = []
        for field_name, field_info in self.schema.model_fields.items():
            desc = field_info.description or field_name
            field_type = field_info.annotation
            fields_desc.append(f"  - {field_name}: {desc}")
        
        fields_text = "\n".join(fields_desc)
        
        # Generate schema JSON example
        schema_json = self.schema.model_json_schema()
        
        prompt = f"""You are an expert at analyzing and validating information for {self.validation_task}.

Analyze the following item: "{item_name}"

Determine the following attributes accurately:
{fields_text}

Return ONLY valid JSON matching the required schema. Be factual and precise."""
        
        return prompt

    def _call_guard(self, item_name: str) -> dict:
        prompt = self._generate_prompt(item_name)
        guard_kwargs = self.adapter.get_params()
        res = self.guard(
            messages=[{"role": "user", "content": prompt}],
            **guard_kwargs
        )
        return res.validated_output


class ConsensusVerifier(HeroVerifier):
    def __init__(self, adapter, schema: Type[BaseModel], validation_task: str = "validation", 
                 iterations=3, threshold=None, logger=None, session_id: str = None, model_name: str = None):
        super().__init__(adapter, schema, validation_task)
        self.iterations = iterations
        
        # Calculate threshold: if threshold is a float < 1, treat as ratio; otherwise as absolute number
        if threshold is None:
            self.threshold = (iterations // 2) + 1
        elif isinstance(threshold, float) and threshold < 1.0:
            # Threshold is a ratio (e.g., 0.6 for 60%)
            import math
            self.threshold = math.ceil(iterations * threshold)
        else:
            # Threshold is an absolute number
            self.threshold = int(threshold)
            
        self.logger = logger
        self.session_id = session_id
        self.model_name = model_name

    def verify(self, item_name: str) -> dict:
        """
        Performs consensus verification.
        Returns a dict with 'consensus' (the result) and 'history' (list of all results).
        """
        history = []
        for i in range(self.iterations):
            try:
                # Add delay to avoid RateLimitError (Groq free tier is sensitive)
                if i > 0:
                    time.sleep(1/559)
                
                res = self._call_guard(item_name)
                # Normalize result to dict if it's an object
                if not isinstance(res, dict):
                    res = res.dict()
                history.append(res)
                
                # Log to database
                if self.logger and self.session_id:
                    self.logger.log_response(
                        session_id=self.session_id,
                        item_name=item_name,
                        iteration_number=i + 1,
                        response_data=res,
                        model_name=self.model_name,
                        adapter_type=self.adapter.__class__.__name__,
                        validation_task=self.validation_task
                    )
                
            except Exception as e:
                error_data = {"error": str(e)}
                history.append(error_data)
                
                # Log error to database
                if self.logger and self.session_id:
                    self.logger.log_response(
                        session_id=self.session_id,
                        item_name=item_name,
                        iteration_number=i + 1,
                        response_data=error_data,
                        model_name=self.model_name,
                        adapter_type=self.adapter.__class__.__name__,
                        validation_task=self.validation_task
                    )

        consensus = self._calculate_consensus(history)
        return {
            "consensus": consensus,
            "history": history
        }

    def _calculate_consensus(self, history: list) -> dict:
        # Filter out errors
        valid_history = [res for res in history if "error" not in res]
        
        if not valid_history:
            return {"error": "No valid responses"}

        # Vote on each field dynamically based on schema
        field_names = list(self.schema.model_fields.keys())
        final_result = {}

        for key in field_names:
            votes = [res.get(key) for res in valid_history if key in res]
            if not votes:
                final_result[key] = None
                continue
            
            # Count votes
            counter = Counter(votes)
            most_common, count = counter.most_common(1)[0]
            
            # Usage of threshold from config/params
            if count >= self.threshold:
                final_result[key] = most_common
            else:
                final_result[key] = "ambiguous"

        return final_result
