#!/usr/bin/env python3
"""Test script to verify French detection improvements."""

import sys
sys.path.insert(0, 'src')

from openai_client import OpenAIClient

# Create a dummy client (we don't need API key for this test)
client = OpenAIClient("dummy_key")

# Test cases from your actual conflicts
test_cases = [
    ("Composants Serveur", True, "Short French with accents"),
    ("Actions Serveur", True, "Short French without accents but with French word"),
    ("Server Components", False, "English"),
    ("Server Actions", False, "English"),
    ('"title": "Composants Serveur"', True, "JSON with French value"),
    ('"title": "Server Components"', False, "JSON with English value"),
    ("Le guide de référence", True, "French with article"),
    ("The reference guide", False, "English with article"),
    ("Documentation pour les composants", True, "Longer French text"),
    ("Documentation for components", False, "Longer English text"),
]

print("Testing French detection with improved heuristics:")
print("=" * 70)

passed = 0
failed = 0

for text, expected, description in test_cases:
    result = client._appears_to_be_french(text)
    status = "✓" if result == expected else "✗"

    if result == expected:
        passed += 1
    else:
        failed += 1

    print(f"{status} {description}")
    print(f"  Text: '{text}'")
    print(f"  Expected: {expected}, Got: {result}")
    print()

print("=" * 70)
print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")

sys.exit(0 if failed == 0 else 1)
