"""
Tests for database logger functionality
"""
import os
import tempfile
from core.db_logger import ValidationLogger

def test_logger_initialization():
    """Test that logger initializes and creates database."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        logger = ValidationLogger(db_path)
        assert os.path.exists(db_path)
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)

def test_session_creation():
    """Test session creation and completion."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        logger = ValidationLogger(db_path)
        session_id = "test_session_001"
        
        logger.start_session(
            session_id=session_id,
            total_items=3,
            consensus_iterations=5,
            consensus_threshold=3,
            validation_task="test task",
            adapter_type="MockAdapter"
        )
        
        logger.complete_session(session_id)
        
        # Verify session exists
        with logger._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM validation_sessions WHERE session_id = ?", (session_id,))
            result = cursor.fetchone()
            assert result is not None
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)

def test_response_logging():
    """Test logging validation responses."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        logger = ValidationLogger(db_path)
        session_id = "test_session_002"
        
        logger.start_session(
            session_id=session_id,
            total_items=1,
            consensus_iterations=1,
            consensus_threshold=1,
            validation_task="test task",
            adapter_type="MockAdapter"
        )
        
        # Log a successful response
        logger.log_response(
            session_id=session_id,
            item_name="test_item",
            iteration_number=1,
            response_data={"field1": True, "field2": "value"},
            model_name="test-model",
            adapter_type="MockAdapter",
            validation_task="test task"
        )
        
        # Verify response was logged
        responses = logger.get_session_responses(session_id)
        assert len(responses) > 0
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)

def test_error_logging():
    """Test logging errors."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        logger = ValidationLogger(db_path)
        session_id = "test_session_003"
        
        logger.start_session(
            session_id=session_id,
            total_items=1,
            consensus_iterations=1,
            consensus_threshold=1,
            validation_task="test task",
            adapter_type="MockAdapter"
        )
        
        # Log an error
        logger.log_response(
            session_id=session_id,
            item_name="test_item",
            iteration_number=1,
            response_data={"error": "Test error message"},
            model_name="test-model",
            adapter_type="MockAdapter",
            validation_task="test task"
        )
        
        # Verify error was logged
        responses = logger.get_session_responses(session_id)
        assert len(responses) > 0
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
