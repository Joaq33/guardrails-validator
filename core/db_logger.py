import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import contextmanager

class ValidationLogger:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Create tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Validation sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS validation_sessions (
                    session_id TEXT PRIMARY KEY,
                    started_at DATETIME NOT NULL,
                    completed_at DATETIME,
                    total_items INTEGER,
                    consensus_iterations INTEGER,
                    consensus_threshold INTEGER,
                    validation_task TEXT,
                    adapter_type TEXT
                )
            """)
            
            # Validation responses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS validation_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    item_name TEXT NOT NULL,
                    iteration_number INTEGER NOT NULL,
                    model_name TEXT,
                    adapter_type TEXT,
                    field_name TEXT NOT NULL,
                    field_value TEXT,
                    is_error BOOLEAN DEFAULT 0,
                    error_message TEXT,
                    validation_task TEXT,
                    response_metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES validation_sessions(session_id)
                )
            """)
            
            # Create index for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_item 
                ON validation_responses(session_id, item_name)
            """)
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def start_session(self, session_id: str, total_items: int, consensus_iterations: int, 
                     consensus_threshold: int, validation_task: str, adapter_type: str):
        """Log the start of a validation session."""
        assert session_id, "session_id cannot be empty"
        assert total_items >= 0, "total_items cannot be negative"
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO validation_sessions 
                (session_id, started_at, total_items, consensus_iterations, 
                 consensus_threshold, validation_task, adapter_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (session_id, datetime.now().isoformat(), total_items, 
                  consensus_iterations, consensus_threshold, validation_task, adapter_type))
            conn.commit()
    
    def complete_session(self, session_id: str):
        """Mark a session as completed."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE validation_sessions 
                SET completed_at = ? 
                WHERE session_id = ?
            """, (datetime.now().isoformat(), session_id))
            conn.commit()
    
    def log_response(self, session_id: str, item_name: str, iteration_number: int,
                    response_data: Dict[str, Any], model_name: Optional[str] = None, 
                    adapter_type: Optional[str] = None, validation_task: Optional[str] = None,
                    metadata: Optional[Dict[str, Any]] = None):
        """
        Log a single validation response.
        """
        assert session_id, "session_id cannot be empty"
        assert item_name, "item_name cannot be empty"
        assert iteration_number > 0, "iteration_number must be positive"
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            timestamp = datetime.now().isoformat()
            
            if "error" in response_data:
                # Log error
                cursor.execute("""
                    INSERT INTO validation_responses 
                    (session_id, timestamp, item_name, iteration_number, model_name,
                     adapter_type, field_name, field_value, is_error, error_message,
                     validation_task, response_metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (session_id, timestamp, item_name, iteration_number, model_name,
                      adapter_type, "error", None, 1, response_data["error"],
                      validation_task, json.dumps(metadata) if metadata else None))
            else:
                # Log each field
                for field_name, field_value in response_data.items():
                    cursor.execute("""
                        INSERT INTO validation_responses 
                        (session_id, timestamp, item_name, iteration_number, model_name,
                         adapter_type, field_name, field_value, is_error, error_message,
                         validation_task, response_metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (session_id, timestamp, item_name, iteration_number, model_name,
                          adapter_type, field_name, str(field_value), 0, None,
                          validation_task, json.dumps(metadata) if metadata else None))
            
            conn.commit()
    
    def get_session_responses(self, session_id: str):
        """Retrieve all responses for a session."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM validation_responses 
                WHERE session_id = ? 
                ORDER BY item_name, iteration_number, field_name
            """, (session_id,))
            return cursor.fetchall()
