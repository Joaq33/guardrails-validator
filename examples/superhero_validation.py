"""
Guardrails Validator - Superhero Capabilities Example

Demonstrates custom display formatting using validation helpers.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples.domains import superhero_config
from examples.validation_helpers import run_validation, print_summary

def display_hero(item, result_data, field_names):
    """Custom display for superhero capabilities."""
    consensus = result_data['consensus']
    
    print(f"Checking {item}...")
    print(f"  ✓ Can fly: {consensus.get('can_fly')}")
    print(f"  ✓ Super strength: {consensus.get('has_super_strength')}")
    print(f"  ✓ Gender: {consensus.get('gender')}\n")

def main():
    print("🛡️ Guardrails Validator - Superhero Example")
    print("=" * 60)
    
    # Run validation with custom display
    session_info = run_validation(
        domain_config=superhero_config,
        iterations=3,
        threshold_ratio=0.67,
        custom_display=display_hero
    )
    
    # Print summary
    print(f"{'=' * 60}")
    print_summary(session_info)

if __name__ == "__main__":
    main()
