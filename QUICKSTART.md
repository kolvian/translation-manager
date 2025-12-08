# Quick Start

## Setup

```bash
cd /Users/epontarelli/translation-manager
source .venv/bin/activate
```

## List Supported Languages

```bash
python3 src/main.py --list-languages
```

## Basic Usage

```bash
# French (default)
python3 src/main.py --codebase-path ../fr.react.dev

# Spanish
python3 src/main.py -p ../es.react.dev -l spanish

# Japanese
python3 src/main.py -p ../ja.react.dev -l ja

# German
python3 src/main.py -p ../de.react.dev -l de
```

## Test First (Dry Run)

```bash
python3 src/main.py -p /path/to/repo --dry-run --max-files 5
```

## Full Run

```bash
python3 src/main.py -p /path/to/repo -l <language>
```

## Custom Environment File

```bash
python3 src/main.py -p /path/to/repo --env-file /path/to/.env.local
```

## Command-Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--codebase-path` | `-p` | Path to the codebase (required) |
| `--language` | `-l` | Target language (default: french) |
| `--list-languages` | | Show all supported languages |
| `--dry-run` | | Analyze only, don't modify files |
| `--max-files` | | Limit number of files to process |
| `--env-file` | | Path to .env.local with API key |
