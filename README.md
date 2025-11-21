# Translation Manager

An intelligent Python tool that automatically resolves merge conflicts between English and French versions of documentation by using OpenAI's GPT-4 for translation analysis and generation.

## Features

- **Automatic Conflict Detection**: Scans your entire codebase for merge conflicts
- **AI-Powered Translation**: Uses OpenAI GPT-4 to compare and translate content
- **French-First Approach**: Keeps existing French translations when they're close enough
- **Smart Resolution**: Only translates when necessary, preserving code and technical terms
- **Safety First**: Flags problematic translations for manual review instead of making mistakes
- **Comprehensive Logging**: Shows detailed progress and results for every conflict

## How It Works

1. **Detection**: Scans for merge conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
2. **Analysis**: For each conflict:
   - Compares the English (incoming) and French (current) versions
   - Asks GPT-4 if the French version is an acceptable translation
   - If close enough → **keeps the French version**
   - If different → **translates the English to French**
3. **Validation**: Ensures translations are in French and don't contain obvious errors
4. **Resolution**: Replaces conflict blocks with the appropriate French text
5. **Safety**: Leaves conflicts unresolved if translation fails or seems incorrect

## Installation

```bash
# Navigate to the project directory
cd translation-manager

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

The script looks for an `.env.local` file with your OpenAI API key. By default, it searches in `../fr.react.dev/.env.local`, but you can specify a custom path.

Your `.env.local` should contain:
```bash
OPENAI_API_KEY='your-api-key-here'
```

## Usage

### Basic Usage

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the script (will scan ../fr.react.dev by default)
python3 src/main.py
```

### Command-Line Options

```bash
# Dry run (analyze but don't modify files)
python3 src/main.py --dry-run

# Specify a custom codebase path
python3 src/main.py --codebase-path /path/to/your/repo

# Specify a custom .env.local location
python3 src/main.py --env-file /path/to/.env.local

# Process only the first N files (useful for testing)
python3 src/main.py --max-files 5

# Combine options
python3 src/main.py --dry-run --max-files 10
```

### Example Output

```
Scanning codebase: /Users/you/fr.react.dev

Found 115 file(s) with merge conflicts.

Analyzing conflicts with OpenAI...
============================================================

[1/115] src/content/learn/keeping-components-pure.md
  Conflict 1/3: ✓ Keeping French (close enough)
  Conflict 2/3: 🔄 Translating... ✓ Done
  Conflict 3/3: ⚠️  Failed - keeping for manual review

============================================================
SUMMARY
============================================================
Total files processed: 115
Total conflicts found: 234
  ✓ Resolved automatically: 198
  ⚠️  Need manual review: 36

Files modified: 98
```

## Safety Guarantees

The script is designed to be conservative and safe:

1. **Never outputs English**: If translation fails, it keeps the conflict for manual review
2. **Never translates code**: Only natural language text is translated; code stays in English
3. **Preserves formatting**: Markdown, code blocks, and structure are maintained
4. **Validates output**: Checks that translations appear to be in French
5. **Dry-run mode**: Test without modifying any files

## Project Structure

```
translation-manager/
├── src/
│   ├── main.py                  # Entry point and orchestration
│   ├── conflict_detector.py     # Finds merge conflicts in files
│   ├── translation_checker.py   # Wraps OpenAI translation checks
│   ├── openai_client.py         # OpenAI API integration
│   ├── file_processor.py        # Resolves conflicts in files
│   └── utils/
│       ├── file_utils.py        # File operations
│       └── diff_utils.py        # Diff utilities
├── config/
│   └── rules.py                 # Configuration and rules
├── tests/
│   ├── test_conflict_detector.py
│   ├── test_translation_checker.py
│   └── test_openai_client.py
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Requirements

- Python 3.8+
- OpenAI API key with GPT-4 access
- Dependencies:
  - openai==0.28.1
  - python-dotenv==0.17.1
  - requests==2.25.1

## Troubleshooting

### "OPENAI_API_KEY not found"
Make sure you have a `.env.local` file with your API key, or specify the path with `--env-file`.

### "Translation appears to still be in English"
The script detected that GPT-4 didn't properly translate to French. The conflict will be left for manual review.

### API Rate Limits
If you hit rate limits, use `--max-files` to process fewer files at once.

## Cost Considerations

This script uses OpenAI's GPT-4 API:
- Each conflict requires 2 API calls (comparison + translation if needed)
- With 115 files and ~200 conflicts, expect ~400 API calls
- Estimated cost: $2-5 per full run

Use `--dry-run` and `--max-files` to control costs while testing.

## License

MIT License
