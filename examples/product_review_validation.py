"""
Product Review Validation Example

Quick demonstration with fewer iterations for fast testing.
Shows how to use custom domain configs with the framework.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
import uuid
import config
from core.verifier import ConsensusVerifier
from core.db_logger import ValidationLogger
from examples.domains import product_review_config

def main():
    print("🛒 Product Review Validation Example")
    print("=" * 60)
    
    # Quick testing settings
    iterations = 3
    threshold_ratio = 0.67  # 2/3 consensus
    
    # Initialize with domain's DB path
    db_path = config.get_db_path(product_review_config)
    logger = ValidationLogger(db_path)
    session_id = f"product_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    adapter = config.get_selected_adapter()
    model_name = adapter.get_params().get("model", "unknown")
    
    print(f"Model: {model_name}")
    print(f"Task: {product_review_config.VALIDATION_TASK}")
    print(f"Reviews: {len(product_review_config.ITEMS_TO_VALIDATE)} items")
    
    import math
    actual_threshold = math.ceil(iterations * threshold_ratio)
    print(f"Consensus: {iterations} iterations, {actual_threshold}/{iterations} threshold\n")
    
    # Start session
    logger.start_session(
        session_id=session_id,
        total_items=len(product_review_config.ITEMS_TO_VALIDATE),
        consensus_iterations=iterations,
        consensus_threshold=actual_threshold,
        validation_task=product_review_config.VALIDATION_TASK,
        adapter_type=adapter.__class__.__name__
    )
    
    # Create verifier
    verifier = ConsensusVerifier(
        adapter=adapter,
        schema=product_review_config.VALIDATION_SCHEMA,
        validation_task=product_review_config.VALIDATION_TASK,
        iterations=iterations,
        threshold=threshold_ratio,
        logger=logger,
        session_id=session_id,
        model_name=model_name
    )
    
    # Process reviews
    print("Processing reviews...")
    print("-" * 60)
    
    for review in product_review_config.ITEMS_TO_VALIDATE:
        print(f"\n📝 Review: \"{review[:50]}...\"" if len(review) > 50 else f"\n📝 Review: \"{review}\"")
        
        result_data = verifier.verify(review)
        consensus = result_data["consensus"]
        history = result_data["history"]
        
        # Show individual calls
        print(f"   Calls: ", end="")
        for i, entry in enumerate(history, 1):
            if "error" not in entry:
                sentiment = "✓" if entry.get('is_positive') else "✗"
                print(f"{sentiment}", end=" ")
        print()
        
        # Show consensus
        print(f"   → Positive: {consensus.get('is_positive')}")
        print(f"   → Mentions Quality: {consensus.get('mentions_quality')}")
        print(f"   → Mentions Price: {consensus.get('mentions_price')}")
    
    logger.complete_session(session_id)
    print(f"\n{'=' * 60}")
    print(f"✅ Complete! Results in: {db_path}")
    print(f"   Session ID: {session_id}")

if __name__ == "__main__":
    main()
