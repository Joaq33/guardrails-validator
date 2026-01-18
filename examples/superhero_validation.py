"""
Guardrails Validator - Superhero Capabilities Example

This example demonstrates how to validate superhero capabilities
using consensus checking across multiple LLM calls.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic import BaseModel, Field
from typing import Literal
import config
from core.verifier import ConsensusVerifier
from core.db_logger import ValidationLogger
from datetime import datetime
import uuid

# Define the schema for superhero capabilities
class HeroCapabilities(BaseModel):
    """Schema for validating superhero capabilities."""
    can_fly: bool = Field(description="Whether the character has the ability to fly")
    has_super_strength: bool = Field(description="Whether the character possesses superhuman strength")
    gender: Literal["male", "female", "unknown"] = Field(description="The character's gender identity")

def main():
    # Override config settings for this example
    heroes = ["Superman", "Wonder Woman", "Batman", "Spider-Man"]
    iterations = 3
    threshold = 2
    
    # Initialize logger
    logger = ValidationLogger("example_validation.db")
    session_id = f"example_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    # Get adapter
    adapter = config.get_selected_adapter()
    model_name = adapter.get_params().get("model", "unknown")
    
    print("🛡️ Guardrails Validator - Superhero Example")
    print(f"Model: {model_name}")
    print(f"Heroes: {', '.join(heroes)}")
    print(f"Consensus: {iterations} iterations, {threshold}/{iterations} threshold\n")
    
    # Start session
    logger.start_session(
        session_id=session_id,
        total_items=len(heroes),
        consensus_iterations=iterations,
        consensus_threshold=threshold,
        validation_task="superhero capabilities",
        adapter_type=adapter.__class__.__name__
    )
    
    # Create verifier
    verifier = ConsensusVerifier(
        adapter=adapter,
        schema=HeroCapabilities,
        validation_task="superhero capabilities",
        iterations=iterations,
        threshold=threshold,
        logger=logger,
        session_id=session_id,
        model_name=model_name
    )
    
    # Validate each hero
    for hero in heroes:
        print(f"Checking {hero}...")
        result_data = verifier.verify(hero)
        consensus = result_data["consensus"]
        
        print(f"  ✓ Can fly: {consensus.get('can_fly')}")
        print(f"  ✓ Super strength: {consensus.get('has_super_strength')}")
        print(f"  ✓ Gender: {consensus.get('gender')}\n")
    
    logger.complete_session(session_id)
    print(f"✅ Complete! Results logged to example_validation.db")

if __name__ == "__main__":
    main()
