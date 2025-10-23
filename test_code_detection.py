#!/usr/bin/env python3
"""Test script to verify code detection improvements."""

import sys
sys.path.insert(0, 'src')

from openai_client import OpenAIClient

# Create a dummy client (we don't need API key for this test)
client = OpenAIClient("dummy_key")

# Test cases for code blocks
test_cases = [
    # (text, expected, description)
    ("// Copiez le tableau!\n  const storiesToDisplay = stories.slice();", True, "Code with French comment"),
    ("// Copy the array!\n  const storiesToDisplay = stories.slice();", True, "Code with English comment (code is valid)"),
    ("const x = 5;", True, "Pure code with no strings"),
    ("function test() { return true; }", True, "Function with no strings"),
    ("""const initialStories = [
  {id: 0, label: "L'histoire d'Ankit" },
  {id: 1, label: "L'histoire de Taylor" },
];""", True, "Code with French strings"),
    ("""const initialStories = [
  {id: 0, label: "Ankit's Story" },
  {id: 1, label: "Taylor's Story" },
];""", False, "Code with English strings"),
    ("let initialStories = []", True, "Code with empty array"),
    ("export default function App() {", True, "Function declaration"),
]

print("Testing code detection with improved heuristics:")
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
    print(f"  Expected: {expected}, Got: {result}")
    if result != expected:
        preview = text[:60] + '...' if len(text) > 60 else text
        print(f"  Text preview: {repr(preview)}")
    print()

print("=" * 70)
print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")

sys.exit(0 if failed == 0 else 1)
