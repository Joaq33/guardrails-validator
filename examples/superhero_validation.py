"""
Guardrails Validator - Superhero Capabilities Example

This example demonstrates how to validate superhero capabilities
using consensus checking across multiple LLM calls.

This example uses the domain config pattern - all domain-specific
settings are in examples/domains/superhero_config.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
import uuid
import config
from core.verifier import ConsensusVerifier
from core.db_logger import ValidationLogger
from examples.domains import superhero_config

def main():
    print("🛡️ Guardrails Validator - Superhero Example")
    
    # Use framework config for iterations/threshold
    # Use domain config for task/items/schema
    iterations = 3
    threshold_ratio = 0.67  # 2/3 consensus
    
    # Initialize logger with domain's DB path
    db_path = config.get_db_path(superhero_config)
    logger = ValidationLogger(db_path)
    session_id = f"example_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    # Get adapter
    adapter = config.get_selected_adapter()
    model_name = adapter.get_params().get("model", "unknown")
    
    print(f"Model: {model_name}")
    print(f"Task: {superhero_config.VALIDATION_TASK}")
    print(f"Heroes: {', '.join(superhero_config.ITEMS_TO_VALIDATE[:3])} ...")
    
    import math
    actual_threshold = math.ceil(iterations * threshold_ratio)
    print(f"Consensus: {iterations} iterations, {actual_threshold}/{iterations} threshold\\n")
    
    # Start session
    logger.start_session(
        session_id=session_id,
        total_items=len(superhero_config.ITEMS_TO_VALIDATE),
        consensus_iterations=iterations,
        consensus_threshold=actual_threshold,
        validation_task=superhero_config.VALIDATION_TASK,
        adapter_type=adapter.__class__.__name__
    )
    
    # Create verifier
    verifier = ConsensusVerifier(
        adapter=adapter,
        schema=superhero_config.VALIDATION_SCHEMA,
        validation_task=superhero_config.VALIDATION_TASK,
        iterations=iterations,
        threshold=threshold_ratio,
        logger=logger,
        session_id=session_id,
        model_name=model_name
    )
    
    # Validate each hero
    for hero in superhero_config.ITEMS_TO_VALIDATE:
        print(f"Checking {hero}...")
        result_data = verifier.verify(hero)
        consensus = result_data["consensus"]
        
        print(f"  ✓ Can fly: {consensus.get('can_fly')}")
        print(f"  ✓ Super strength: {consensus.get('has_super_strength')}")
        print(f"  ✓ Gender: {consensus.get('gender')}\\n")
    
    logger.complete_session(session_id)
    print(f"✅ Complete! Results logged to {db_path}")

if __name__ == "__main__":
    main()
