#!/usr/bin/env python3
"""
Guardrails Validator - Main CLI

Usage:
    uv run main.py --domain examples.domains.superhero_config
    uv run main.py  # Uses default superhero config
"""
import sys
import uuid
import argparse
import importlib
from datetime import datetime
import config
from core.verifier import ConsensusVerifier
from core.db_logger import ValidationLogger

def run_validation(domain_config):
    """Run validation with the provided domain configuration."""
    print("Guardrails Validator - Generic Mode")
    
    # 1. Initialize database logger with domain-specific path
    db_path = config.get_db_path(domain_config)
    logger = ValidationLogger(db_path)
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    # 2. Load adapter from framework config
    adapter = config.get_selected_adapter()
    adapter_name = adapter.__class__.__name__
    
    # Get model name from adapter if available
    model_name = adapter.get_params().get("model", "unknown")
    
    print(f"Using Adapter: {adapter_name}")
    print(f"Model: {model_name}")
    print(f"Session ID: {session_id}") 
    print(f"Validation Task: {domain_config.VALIDATION_TASK}")
    print(f"Items to validate: {', '.join(domain_config.ITEMS_TO_VALIDATE)}")
    
    # Calculate actual threshold for display
    import math
    actual_threshold = math.ceil(config.CONSENSUS_ITERATIONS * config.CONSENSUS_THRESHOLD_RATIO)
    print(f"Consensus: {config.CONSENSUS_ITERATIONS} iterations, Threshold: {actual_threshold}/{config.CONSENSUS_ITERATIONS} ({config.CONSENSUS_THRESHOLD_RATIO*100:.0f}%)\\n")

    # 3. Start session logging
    logger.start_session(
        session_id=session_id,
        total_items=len(domain_config.ITEMS_TO_VALIDATE),
        consensus_iterations=config.CONSENSUS_ITERATIONS,
        consensus_threshold=actual_threshold,
        validation_task=domain_config.VALIDATION_TASK,
        adapter_type=adapter_name
    )

    # 4. Logic Instantiation (schema-agnostic)
    verifier = ConsensusVerifier(
        adapter, 
        schema=domain_config.VALIDATION_SCHEMA,
        validation_task=domain_config.VALIDATION_TASK,
        iterations=config.CONSENSUS_ITERATIONS,
        threshold=config.CONSENSUS_THRESHOLD_RATIO,
        logger=logger,
        session_id=session_id,
        model_name=model_name
    )
    
    # Get field names dynamically from schema
    field_names = list(domain_config.VALIDATION_SCHEMA.model_fields.keys())
    
    # Print header
    header = f"{'Item':<20}"
    for field in field_names:
        header += f" {field:<15}"
    print(header)
    print("-" * (20 + 15 * len(field_names)))
        
    for item in domain_config.ITEMS_TO_VALIDATE:
        try:
            print(f"Checking {item}...", end="\\n")
            
            # 5. Execution delegation
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
            print(f"  Result: {consensus_str}\\n")
            
        except Exception as e:
            print(f"{item:<20} ERROR: {str(e)[:60]}")

    # 6. Complete session logging
    logger.complete_session(session_id)
    print(f"\\nVerification Complete!")
    print(f"Results logged to database: {db_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Guardrails Validator - Generic LLM validation with consensus",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run main.py --domain examples.domains.superhero_config
  uv run main.py  # Uses default superhero config
        """
    )
    parser.add_argument(
        '--domain',
        type=str,
        default='examples.domains.superhero_config',
        help='Python module path to domain configuration (default: examples.domains.superhero_config)'
    )
    
    args = parser.parse_args()
    
    # Import domain configuration
    try:
        domain_config = importlib.import_module(args.domain)
        
        # Validate required attributes
        required_attrs = ['VALIDATION_TASK', 'ITEMS_TO_VALIDATE', 'VALIDATION_SCHEMA']
        missing = [attr for attr in required_attrs if not hasattr(domain_config, attr)]
        if missing:
            print(f"Error: Domain config missing required attributes: {', '.join(missing)}")
            sys.exit(1)
            
    except ImportError as e:
        print(f"Error: Could not import domain config '{args.domain}': {e}")
        print("\\nMake sure the module path is correct and uses dot notation.")
        sys.exit(1)
    
    # Run validation
    run_validation(domain_config)

if __name__ == '__main__':
    main()
