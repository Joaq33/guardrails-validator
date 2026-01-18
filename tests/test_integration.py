"""
Integration tests for the validation system
"""

import tempfile
from models import HeroCapabilities
from model_adapters.mock_adapter import MockAdapter
from core.verifier import ConsensusVerifier
from core.db_logger import ValidationLogger


def test_consensus_with_mock_adapter():
    """Test consensus verification with MockAdapter."""
    adapter = MockAdapter()
    verifier = ConsensusVerifier(
        adapter=adapter,
        schema=HeroCapabilities,
        validation_task="test superheroes",
        iterations=3,
        threshold=2,
    )

    result = verifier.verify("Superman")

    assert "consensus" in result
    assert "history" in result
    assert len(result["history"]) == 3


def test_full_validation_workflow():
    """Test complete validation workflow with logging."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_path = f.name

    try:
        # Setup
        logger = ValidationLogger(db_path)
        session_id = "integration_test_001"
        adapter = MockAdapter()

        # Start session
        logger.start_session(
            session_id=session_id,
            total_items=1,
            consensus_iterations=3,
            consensus_threshold=2,
            validation_task="test task",
            adapter_type="MockAdapter",
        )

        # Create verifier with logger
        verifier = ConsensusVerifier(
            adapter=adapter,
            schema=HeroCapabilities,
            validation_task="test superheroes",
            iterations=3,
            threshold=2,
            logger=logger,
            session_id=session_id,
            model_name="mock-model",
        )

        # Run verification
        result = verifier.verify("Batman")

        # Complete session
        logger.complete_session(session_id)

        # Verify results
        assert result["consensus"] is not None
        responses = logger.get_session_responses(session_id)
        assert len(responses) > 0

    finally:
        import os

        if os.path.exists(db_path):
            os.remove(db_path)
