"""
Product Review Validation Example

Demonstrates custom display formatting using validation helpers.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples.domains import product_review_config
from examples.validation_helpers import run_validation, print_header, print_summary

def display_review(item, result_data, field_names):
    """Custom display for product reviews."""
    consensus = result_data['consensus']
    history = result_data['history']
    
    # Show review text
    review_text = item[:50] + "..." if len(item) > 50 else item
    print(f"\n📝 Review: \"{review_text}\"")
    
    # Show individual calls with ✓/✗ symbols
    print(f"   Calls: ", end="")
    for entry in history:
        if "error" not in entry:
            sentiment = "✓" if entry.get('is_positive') else "✗"
            print(f"{sentiment}", end=" ")
    print()
    
    # Show consensus results
    print(f"   → Positive: {consensus.get('is_positive')}")
    print(f"   → Mentions Quality: {consensus.get('mentions_quality')}")
    print(f"   → Mentions Price: {consensus.get('mentions_price')}")

def main():
    print("🛒 Product Review Validation Example")
    print("=" * 60)
    
    # Run validation with custom display
    session_info = run_validation(
        domain_config=product_review_config,
        iterations=3,
        threshold_ratio=0.67,
        custom_display=display_review
    )
    
    # Print summary
    print(f"\n{'=' * 60}")
    print_summary(session_info)

if __name__ == "__main__":
    main()
