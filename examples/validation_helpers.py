"""
Validation helpers for running validations with custom display logic.
"""

import uuid
from datetime import datetime
import math
import config
from core.verifier import ConsensusVerifier
from core.db_logger import ValidationLogger


def run_validation(
    domain_config, iterations=None, threshold_ratio=None, custom_display=None
):
    """
    Run validation with a domain config and optional custom display logic.

    Args:
        domain_config: Module with VALIDATION_TASK, ITEMS_TO_VALIDATE, VALIDATION_SCHEMA
        iterations: Number of consensus iterations (uses framework default if None)
        threshold_ratio: Consensus threshold ratio (uses framework default if None)
        custom_display: Optional function(item, result_data, field_names) for custom output

    Returns:
        dict with session_id, db_path, results
    """
    # Validation of domain_config
    assert hasattr(domain_config, "VALIDATION_TASK"), (
        "domain_config must have VALIDATION_TASK"
    )
    assert hasattr(domain_config, "ITEMS_TO_VALIDATE"), (
        "domain_config must have ITEMS_TO_VALIDATE"
    )
    assert hasattr(domain_config, "VALIDATION_SCHEMA"), (
        "domain_config must have VALIDATION_SCHEMA"
    )
    assert len(domain_config.ITEMS_TO_VALIDATE) > 0, "ITEMS_TO_VALIDATE cannot be empty"

    # Use framework defaults if not specified
    iterations = iterations or config.CONSENSUS_ITERATIONS
    assert iterations > 0, "iterations must be positive"
    threshold_ratio = threshold_ratio or config.CONSENSUS_THRESHOLD_RATIO
    assert 0.0 <= threshold_ratio <= 1.0, "threshold_ratio must be between 0.0 and 1.0"

    # Setup
    db_path = config.get_db_path(domain_config)
    logger = ValidationLogger(db_path)
    session_id = f"{domain_config.VALIDATION_TASK.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

    adapter = config.get_selected_adapter()
    model_name = adapter.get_params().get("model", "unknown")
    actual_threshold = math.ceil(iterations * threshold_ratio)

    # Start session
    logger.start_session(
        session_id=session_id,
        total_items=len(domain_config.ITEMS_TO_VALIDATE),
        consensus_iterations=iterations,
        consensus_threshold=actual_threshold,
        validation_task=domain_config.VALIDATION_TASK,
        adapter_type=adapter.__class__.__name__,
    )

    # Create verifier
    verifier = ConsensusVerifier(
        adapter=adapter,
        schema=domain_config.VALIDATION_SCHEMA,
        validation_task=domain_config.VALIDATION_TASK,
        iterations=iterations,
        threshold=threshold_ratio,
        logger=logger,
        session_id=session_id,
        model_name=model_name,
    )

    # Get field names
    field_names = list(domain_config.VALIDATION_SCHEMA.model_fields.keys())

    # Process items
    results = []
    for item in domain_config.ITEMS_TO_VALIDATE:
        result_data = verifier.verify(item)
        results.append(
            {
                "item": item,
                "consensus": result_data["consensus"],
                "history": result_data["history"],
            }
        )

        # Custom display if provided
        if custom_display:
            custom_display(item, result_data, field_names)

    # Complete session
    logger.complete_session(session_id)

    return {
        "session_id": session_id,
        "db_path": db_path,
        "results": results,
        "model_name": model_name,
        "iterations": iterations,
        "threshold": actual_threshold,
    }


def print_header(domain_config, model_name, iterations, threshold):
    """Print a standard validation header."""
    print(f"Validation: {domain_config.VALIDATION_TASK}")
    print(f"Model: {model_name}")
    print(f"Items: {len(domain_config.ITEMS_TO_VALIDATE)}")
    print(f"Consensus: {iterations} iterations, {threshold}/{iterations} threshold\n")


def print_summary(session_info):
    """Print a standard validation summary."""
    print(f"\n✅ Complete! Results in: {session_info['db_path']}")
    print(f"   Session ID: {session_info['session_id']}")
