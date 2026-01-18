"""
Tests for MockAdapter functionality
"""
from adapters.mock_adapter import MockAdapter

def test_mock_adapter_initialization():
    """Test MockAdapter can be initialized."""
    adapter = MockAdapter()
    assert adapter is not None

def test_mock_adapter_get_params():
    """Test MockAdapter returns correct params."""
    adapter = MockAdapter()
    params = adapter.get_params()
    
    assert "llm_api" in params
    assert params["llm_api"] == adapter

def test_mock_adapter_superman():
    """Test MockAdapter returns correct data for Superman."""
    adapter = MockAdapter()
    result = adapter(prompt="Superman")
    
    assert "can_fly" in result
    assert "true" in result.lower()
    assert "super_strength" in result.lower() or "has_super_strength" in result.lower()

def test_mock_adapter_batman():
    """Test MockAdapter returns correct data for Batman."""
    adapter = MockAdapter()
    result = adapter(prompt="Batman")
    
    assert "can_fly" in result
    assert "false" in result.lower()
