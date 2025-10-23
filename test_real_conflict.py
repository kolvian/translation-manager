#!/usr/bin/env python3
"""Test with a real conflict that's failing."""

import sys
import os
sys.path.insert(0, 'src')

from dotenv import load_dotenv
from openai_client import OpenAIClient

# Load API key
env_path = os.path.join(os.path.dirname(__file__), '..', 'fr.react.dev', '.env.local')
load_dotenv(env_path)
openai_api_key = os.getenv('OPENAI_API_KEY')

if not openai_api_key:
    print("Error: OPENAI_API_KEY not found")
    sys.exit(1)

client = OpenAIClient(openai_api_key)

# Test with the actual failing conflict
english_text = """const initialStories = [
  {id: 0, label: "Ankit's Story" },
  {id: 1, label: "Taylor's Story" },
];"""

print("Testing translation of code with English strings...")
print("=" * 70)
print("ENGLISH INPUT:")
print(english_text)
print("\n" + "=" * 70)
print("Attempting translation...\n")

result = client.translate_to_french(english_text)

if result:
    print("✓ Translation succeeded!")
    print("\nFRENCH OUTPUT:")
    print(result)
    print("\n" + "=" * 70)
    print(f"Appears to be French: {client._appears_to_be_french(result)}")
else:
    print("✗ Translation failed!")
