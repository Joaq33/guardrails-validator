"""
Tests for Pydantic models
"""
from models import HeroCapabilities

def test_hero_capabilities_creation():
    """Test HeroCapabilities model can be created."""
    hero = HeroCapabilities(
        can_fly=True,
        has_super_strength=True,
        gender="male"
    )
    
    assert hero.can_fly is True
    assert hero.has_super_strength is True
    assert hero.gender == "male"

def test_hero_capabilities_validation():
    """Test HeroCapabilities validates gender field."""
    # Valid genders should work
    for gender in ["male", "female", "unknown"]:
        hero = HeroCapabilities(
            can_fly=False,
            has_super_strength=False,
            gender=gender
        )
        assert hero.gender == gender

def test_hero_capabilities_field_descriptions():
    """Test that field descriptions exist."""
    fields = HeroCapabilities.model_fields
    
    assert "can_fly" in fields
    assert "has_super_strength" in fields
    assert "gender" in fields
    
    # Check descriptions exist
    assert fields["can_fly"].description is not None
    assert fields["has_super_strength"].description is not None
    assert fields["gender"].description is not None
