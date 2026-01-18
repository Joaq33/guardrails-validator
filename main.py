#!/usr/bin/env python3
"""
Guardrails Validator - Main CLI

Usage:
    uv run main.py --domain examples.domains.superhero_config
    uv run main.py  # Uses default superhero config
"""
import sys
import argparse
import importlib
from examples.validation_helpers import run_validation, print_summary


def default_display(item, result_data, field_names):
    """Default table-like display for CLI."""
    consensus = result_data['consensus']
    history = result_data['history']

    print(f"Checking {item}...", end="\n")

    # Display Logs
    print("  [Logs]")
    for i, entry in enumerate(history, 1):
        if "error" in entry:
            print(f"    Call {i}: ERROR - {entry['error'][:80]}")
            continue

        # Display all fields dynamically
        field_str = ", ".join([f"{k}={entry.get(k, 'N/A')}" for k in field_names])
        print(f"    Call {i}: {field_str}")

    # Display Consensus
    consensus_str = ", ".join([f"{k}={consensus.get(k, 'N/A')}" for k in field_names])
    print("  [Consensus]")
    print(f"  Result: {consensus_str}\n")


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
        print("\nMake sure the module path is correct and uses dot notation.")
        sys.exit(1)

    print("Guardrails Validator - Generic Mode")
    print("=" * 60)

    # Run validation with default CLI display
    # Use global config for iterations/threshold
    session_info = run_validation(
        domain_config=domain_config,
        custom_display=default_display
    )

    print("-" * 60)
    print_summary(session_info)


if __name__ == '__main__':
    main()
