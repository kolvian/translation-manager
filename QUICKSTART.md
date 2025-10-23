# Quick Start Guide

## Prerequisites

1. Python 3.8 or higher installed
2. OpenAI API key with GPT-4 access
3. A repository with merge conflicts (English incoming, French current)

## Setup (5 minutes)

```bash
# 1. Navigate to the translation-manager directory
cd /Users/epontarelli/translation-manager

# 2. Activate the virtual environment
source .venv/bin/activate

# 3. Verify the .env.local file exists with your API key
# Default location: ../fr.react.dev/.env.local
# It should contain: OPENAI_API_KEY='your-key-here'
```

## Usage Examples

### Test Run (Recommended First Step)

```bash
# Analyze first 5 files without making changes
python3 src/main.py --dry-run --max-files 5
```

This will:
- Show you what conflicts exist
- Test the API connection
- Give you a preview of what will happen
- Won't modify any files

### Process a Small Batch

```bash
# Process first 10 files
python3 src/main.py --max-files 10
```

### Full Run

```bash
# Process all conflicts in the codebase
python3 src/main.py
```

### Custom Repository

```bash
# Process a different repository
python3 src/main.py --codebase-path /path/to/repo --env-file /path/to/.env.local
```

## What the Script Does

For each merge conflict:

1. **Analyzes**: Compares English (incoming) vs French (current)
2. **Decides**:
   - If French is a good translation → ✓ Keeps French version
   - If significantly different → 🔄 Translates English to French
   - If translation fails → ⚠️ Leaves conflict for manual review
3. **Validates**: Ensures output is in French and makes sense
4. **Resolves**: Removes conflict markers and writes the chosen version

## Understanding the Output

```
[1/115] src/content/learn/example.md
  Conflict 1/3: ✓ Keeping French (close enough)
  Conflict 2/3: 🔄 Translating... ✓ Done
  Conflict 3/3: ⚠️  Failed - keeping for manual review
```

- **✓ Keeping French**: The French translation is good, keeping it
- **🔄 Translating... ✓ Done**: Translated English to French successfully
- **⚠️ Failed**: Could not translate safely, needs manual review

## After Running

```bash
# 1. Check what changed
git status
git diff

# 2. Find remaining conflicts (if any)
git diff --check

# 3. Test your changes thoroughly

# 4. Commit when satisfied
git add .
git commit -m "Resolve merge conflicts with AI translation"
```

## Tips & Best Practices

### Start Small
Always use `--dry-run` and `--max-files` first to test

### Monitor Costs
- Each conflict ≈ 2 API calls
- 100 conflicts ≈ $1-2 in API costs
- Use `--max-files` to control batch size

### Manual Review Still Needed
The script is conservative - it will flag anything uncertain:
- Complex technical content
- Mixed code and text
- Ambiguous translations

These are intentionally left for human review.

### Watch for Patterns
If many files fail with the same issue, you might need to:
- Adjust the codebase path
- Check file permissions
- Verify API key has GPT-4 access

## Troubleshooting

### "No conflicts found"
- Make sure you're in a Git repository with merge conflicts
- Check that the codebase path is correct
- Verify files have standard conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)

### "OPENAI_API_KEY not found"
```bash
# Check if .env.local exists and has the key
cat ../fr.react.dev/.env.local

# Or specify a custom path
python3 src/main.py --env-file /path/to/.env.local
```

### "Translation appears to still be in English"
This is a safety check. The script detected English in the output and kept the conflict for manual review.

### Rate Limit Errors
```bash
# Process in smaller batches
python3 src/main.py --max-files 20

# Wait a minute, then continue with the next batch
python3 src/main.py --max-files 20  # processes next 20
```

## Need Help?

1. Check the main README.md for detailed documentation
2. Review the example output in the test runs
3. Use `--dry-run` to experiment safely
4. Start with `--max-files 1` to debug specific issues

## Common Workflows

### First Time Setup
```bash
cd /Users/epontarelli/translation-manager
source .venv/bin/activate
python3 src/main.py --dry-run --max-files 3  # Test run
python3 src/main.py --max-files 10            # Small batch
git diff                                       # Review changes
```

### Regular Use
```bash
cd /Users/epontarelli/translation-manager
source .venv/bin/activate
python3 src/main.py                            # Full run
git diff --check                               # Find remaining conflicts
# Manually resolve flagged conflicts
git add . && git commit -m "Resolve conflicts"
```

### Debugging Issues
```bash
# Test with minimal scope
python3 src/main.py --dry-run --max-files 1

# Check specific file
grep -r "<<<<<<< HEAD" ../fr.react.dev/src/specific-file.md

# Verify API access
python3 -c "import openai; print(openai.__version__)"
```
