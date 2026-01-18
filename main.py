import sys
import uuid
from datetime import datetime
import config
from core.verifier import ConsensusVerifier
from core.db_logger import ValidationLogger

def main():
    print("Guardrails Validator - Generic Mode")
    
    # 1. Initialize database logger
    logger = ValidationLogger(config.DATABASE_PATH)
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    # 2. Load config
    adapter = config.get_selected_adapter()
    adapter_name = adapter.__class__.__name__
    
    # Get model name from adapter if available
    model_name = adapter.get_params().get("model", "unknown")
    
    print(f"Using Adapter: {adapter_name}")
    print(f"Model: {model_name}")
    print(f"Session ID: {session_id}") 
    print(f"Validation Task: {config.VALIDATION_TASK}")
    print(f"Items to validate: {', '.join(config.ITEMS_TO_VALIDATE)}")
    # Calculate actual threshold for display
    import math
    actual_threshold = math.ceil(config.CONSENSUS_ITERATIONS * config.CONSENSUS_THRESHOLD_RATIO)
    print(f"Consensus: {config.CONSENSUS_ITERATIONS} iterations, Threshold: {actual_threshold}/{config.CONSENSUS_ITERATIONS} ({config.CONSENSUS_THRESHOLD_RATIO*100:.0f}%)\n")

    # 3. Start session logging
    logger.start_session(
        session_id=session_id,
        total_items=len(config.ITEMS_TO_VALIDATE),
        consensus_iterations=config.CONSENSUS_ITERATIONS,
        consensus_threshold=actual_threshold,
        validation_task=config.VALIDATION_TASK,
        adapter_type=adapter_name
    )

    # 4. Logic Instantiation (schema-agnostic)
    verifier = ConsensusVerifier(
        adapter, 
        schema=config.VALIDATION_SCHEMA,
        validation_task=config.VALIDATION_TASK,
        iterations=config.CONSENSUS_ITERATIONS,
        threshold=config.CONSENSUS_THRESHOLD_RATIO,
        logger=logger,
        session_id=session_id,
        model_name=model_name
    )
    
    # Get field names dynamically from schema
    field_names = list(config.VALIDATION_SCHEMA.model_fields.keys())
    
    # Print header
    header = f"{'Item':<20}"
    for field in field_names:
        header += f" {field:<15}"
    print(header)
    print("-" * (20 + 15 * len(field_names)))
        
    for item in config.ITEMS_TO_VALIDATE:
        try:
            print(f"Checking {item}...", end="\n")
            
            # 3. Execution delegation
            result_data = verifier.verify(item)
            consensus = result_data["consensus"]
            history = result_data["history"]

            # Display Logs
            print(f"  [Logs]")
            for i, entry in enumerate(history, 1):
                if "error" in entry:
                    print(f"    Call {i}: ERROR - {entry['error'][:80]}")
                    continue
                
                # Display all fields dynamically
                field_str = ", ".join([f"{k}={entry.get(k, 'N/A')}" for k in field_names])
                print(f"    Call {i}: {field_str}")
            
            # Display Consensus
            consensus_str = ", ".join([f"{k}={consensus.get(k, 'N/A')}" for k in field_names])
            print(f"  [Consensus]")
            print(f"  Result: {consensus_str}\n")
            
        except Exception as e:
            print(f"{item:<20} ERROR: {str(e)[:60]}")

    # 5. Complete session logging
    logger.complete_session(session_id)
    print(f"\nVerification Complete!")
    print(f"Results logged to database: {config.DATABASE_PATH}")

if __name__ == '__main__':
    main()
