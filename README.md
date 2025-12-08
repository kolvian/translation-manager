# Translation Manager

An intelligent Python tool that automatically resolves merge conflicts between English and translated versions of documentation by using OpenAI's GPT for translation analysis and generation. Supports 12+ languages.

## Features

- **Automatic Conflict Detection**: Scans your entire codebase for merge conflicts
- **AI-Powered Translation**: Uses OpenAI GPT to compare and translate content
- **Multi-Language Support**: Supports 12+ languages including French, Spanish, German, Japanese, Chinese, and more
- **Smart Resolution**: Only translates when necessary, preserving code and technical terms
- **Translation-First Approach**: Keeps existing translations when they're close enough
- **Safety First**: Flags problematic translations for manual review instead of making mistakes
- **Comprehensive Logging**: Shows detailed progress and results for every conflict

## Supported Languages

| Language   | Code | Native Name |
|------------|------|-------------|
| French     | fr   | Français    |
| Spanish    | es   | Español     |
| German     | de   | Deutsch     |
| Portuguese | pt   | Português   |
| Italian    | it   | Italiano    |
| Japanese   | ja   | 日本語       |
| Chinese    | zh   | 中文         |
| Korean     | ko   | 한국어       |
| Russian    | ru   | Русский     |
| Arabic     | ar   | العربية     |
| Dutch      | nl   | Nederlands  |
| Polish     | pl   | Polski      |

Run `python3 src/main.py --list-languages` to see all supported languages.

## How It Works

1. **Detection**: Scans for merge conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
2. **Analysis**: For each conflict:
   - Compares the English (incoming) and translated (current) versions
   - Asks GPT if the translated version is an acceptable translation
   - If close enough → **keeps the existing translation**
   - If different → **translates the English to your target language**
3. **Validation**: Ensures translations are in the correct language and don't contain obvious errors
4. **Resolution**: Replaces conflict blocks with the appropriate translated text
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

The script looks for an `.env.local` file with your OpenAI API key. It searches in:
1. The codebase directory you specify
2. The translation-manager directory

Your `.env.local` should contain:
```bash
OPENAI_API_KEY='your-api-key-here'
```

## Usage

### Basic Usage

```bash
# Activate virtual environment
source .venv/bin/activate

# Translate to French (default language)
python3 src/main.py --codebase-path /path/to/fr.react.dev

# Translate to Spanish
python3 src/main.py --codebase-path /path/to/es.react.dev --language spanish

# Translate to Japanese
python3 src/main.py --codebase-path /path/to/ja.react.dev -l ja
```

### Command-Line Options

```bash
# Required: Specify the codebase path
python3 src/main.py --codebase-path /path/to/your/repo

# Specify target language (default: french)
python3 src/main.py -p /path/to/repo --language german
python3 src/main.py -p /path/to/repo -l de

# List all supported languages
python3 src/main.py --list-languages

# Dry run (analyze but don't modify files)
python3 src/main.py -p /path/to/repo --dry-run

# Specify a custom .env.local location
python3 src/main.py -p /path/to/repo --env-file /path/to/.env.local

# Process only the first N files (useful for testing)
python3 src/main.py -p /path/to/repo --max-files 5

# Combine options
python3 src/main.py -p ../es.react.dev -l spanish --dry-run --max-files 10
```

### Example Output

```
Translation Manager
============================================================
Codebase:        /Users/you/es.react.dev
Target language: Spanish (es)
Mode:            DRY RUN (no files will be modified)
============================================================

Found 115 file(s) with merge conflicts.

Analyzing conflicts with OpenAI (translating to Spanish)...
============================================================

[1/115] src/content/learn/keeping-components-pure.md
  Conflict 1/3: Keeping Spanish (close enough)
  Conflict 2/3: Translating... Done
  Conflict 3/3: Failed - keeping for manual review

============================================================
SUMMARY
============================================================
Target language:         Spanish (es)
Total files processed:   115
Total conflicts found:   234
  Resolved automatically: 198
  Need manual review:     36

Files modified: 98
```

## Safety Guarantees

The script is designed to be conservative and safe:

1. **Never outputs English**: If translation fails, it keeps the conflict for manual review
2. **Never translates code**: Only natural language text is translated; code stays in English
3. **Preserves formatting**: Markdown, code blocks, and structure are maintained
4. **Validates output**: Checks that translations appear to be in the target language
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
│   └── rules.py                 # Language configs and rules
├── tests/
│   ├── test_conflict_detector.py
│   ├── test_translation_checker.py
│   └── test_openai_client.py
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Requirements

- Python 3.8+
- OpenAI API key with GPT access
- Dependencies:
  - openai>=2.0.0
  - python-dotenv==0.17.1
  - requests==2.25.1

## Troubleshooting

### "OPENAI_API_KEY not found"
Make sure you have a `.env.local` file with your API key in either the codebase directory or the translation-manager directory, or specify the path with `--env-file`.

### "Unsupported language"
Run `python3 src/main.py --list-languages` to see all supported languages. Use either the language name (e.g., "french") or the language code (e.g., "fr").

### "Translation appears to still be in English"
The script detected that GPT didn't properly translate to the target language. The conflict will be left for manual review.

### API Rate Limits
If you hit rate limits, use `--max-files` to process fewer files at once.

## Cost Considerations

This script uses OpenAI's GPT API:
- Each conflict requires 2 API calls (comparison + translation if needed)
- With 115 files and ~200 conflicts, expect ~400 API calls
- Estimated cost: $2-5 per full run

Use `--dry-run` and `--max-files` to control costs while testing.

## Adding New Languages

To add support for a new language, edit `config/rules.py` and add an entry to `SUPPORTED_LANGUAGES`:

```python
'your_language': {
    'code': 'xx',  # ISO 639-1 code
    'name': 'Your Language',
    'native_name': 'Native Name',
    'accented_chars': ['á', 'é', ...],  # Unique characters
    'common_words': [' word1 ', ' word2 ', ...],  # Common words with spaces
    'string_indicators': ['indicator1', 'indicator2'],  # Words in code strings
    'keywords': ['kw1', 'kw2', ...],  # Keywords for quick detection
}
```

For non-Latin scripts, add `char_ranges` with Unicode code point ranges:
```python
'char_ranges': [(0x0400, 0x04FF)],  # Example: Cyrillic range
```

## License

MIT License
