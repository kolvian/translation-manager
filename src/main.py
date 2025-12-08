import os
import sys
import argparse
from dotenv import load_dotenv

# Add parent directory to path to import config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config.rules import SUPPORTED_LANGUAGES, list_supported_languages, get_language_config

from conflict_detector import ConflictDetector
from translation_checker import TranslationChecker
from openai_client import OpenAIClient
from file_processor import FileProcessor


def parse_args():
    parser = argparse.ArgumentParser(
        description='Automatically resolve merge conflicts by translating English to your target language using OpenAI.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Translate to French (default)
  python3 src/main.py --codebase-path /path/to/fr.react.dev

  # Translate to Spanish
  python3 src/main.py --codebase-path /path/to/es.react.dev --language spanish

  # Translate to Japanese with dry run
  python3 src/main.py --codebase-path /path/to/ja.react.dev -l ja --dry-run

  # List all supported languages
  python3 src/main.py --list-languages
'''
    )
    parser.add_argument(
        '--codebase-path', '-p',
        type=str,
        required=False,
        help='Path to the codebase to scan for conflicts (required unless using --list-languages)'
    )
    parser.add_argument(
        '--language', '-l',
        type=str,
        default='french',
        help='Target language for translation (default: french). Use language name or code (e.g., "french", "fr", "spanish", "es")'
    )
    parser.add_argument(
        '--list-languages',
        action='store_true',
        help='List all supported languages and exit'
    )
    parser.add_argument(
        '--env-file',
        type=str,
        help='Path to .env.local file with OPENAI_API_KEY (default: looks in codebase directory)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Analyze conflicts but do not write changes to files'
    )
    parser.add_argument(
        '--max-files',
        type=int,
        help='Maximum number of files to process (useful for testing)'
    )
    return parser.parse_args()


def print_supported_languages():
    """Print a formatted list of supported languages."""
    print("Supported Languages:")
    print("=" * 50)
    print(f"{'Name':<15} {'Code':<6} {'Native Name'}")
    print("-" * 50)
    for key, name, code in list_supported_languages():
        config = SUPPORTED_LANGUAGES[key]
        native = config.get('native_name', name)
        print(f"{name:<15} {code:<6} {native}")
    print("=" * 50)
    print("\nUse --language <name> or --language <code>")
    print("Example: --language french  or  --language fr")


def main():
    args = parse_args()

    # Handle --list-languages
    if args.list_languages:
        print_supported_languages()
        return 0

    # Validate target language
    lang_config = get_language_config(args.language)
    if not lang_config:
        print(f"Error: Unsupported language '{args.language}'")
        print("\nRun with --list-languages to see all supported languages.")
        return 1

    lang_name = lang_config['name']
    lang_code = lang_config['code']

    # Validate codebase path
    if not args.codebase_path:
        print("Error: --codebase-path is required")
        print("\nUsage: python3 src/main.py --codebase-path /path/to/your/repo")
        print("\nExamples:")
        print("  python3 src/main.py --codebase-path ../fr.react.dev")
        print("  python3 src/main.py --codebase-path ../es.react.dev --language spanish")
        return 1

    codebase_path = os.path.abspath(args.codebase_path)

    if not os.path.exists(codebase_path):
        print(f"Error: Codebase path does not exist: {codebase_path}")
        return 1

    # Load environment variables from .env.local
    if args.env_file:
        env_path = args.env_file
    else:
        # Look for .env.local in the codebase directory first, then current directory
        env_path = os.path.join(codebase_path, '.env.local')
        if not os.path.exists(env_path):
            env_path = os.path.join(os.path.dirname(__file__), '..', '.env.local')

    load_dotenv(env_path)
    openai_api_key = os.getenv('OPENAI_API_KEY')

    if not openai_api_key:
        print(f"Error: OPENAI_API_KEY not found")
        print(f"Searched in: {env_path}")
        print("\nPlease set the API key in a .env.local file or specify with --env-file")
        return 1

    print(f"Translation Manager")
    print("=" * 60)
    print(f"Codebase:        {codebase_path}")
    print(f"Target language: {lang_name} ({lang_code})")
    if args.dry_run:
        print("Mode:            DRY RUN (no files will be modified)")
    print("=" * 60)
    print()

    # Initialize components with target language
    conflict_detector = ConflictDetector(codebase_path, target_language=args.language)
    translation_checker = TranslationChecker()
    openai_client = OpenAIClient(openai_api_key, target_language=args.language)
    file_processor = FileProcessor()

    # Step 1: Detect merge conflicts
    conflicts = conflict_detector.find_merge_conflicts()

    if not conflicts:
        print(f"No merge conflicts found in the codebase.")
        return 0

    # Limit files if requested
    if args.max_files and len(conflicts) > args.max_files:
        print(f"Limiting to first {args.max_files} files (found {len(conflicts)} total)")
        conflicts = conflicts[:args.max_files]

    print(f"Found {len(conflicts)} file(s) with merge conflicts.\n")

    # Step 2: Check translation closeness and manage translations
    print(f"Analyzing conflicts with OpenAI (translating to {lang_name})...")
    print("=" * 60)

    for idx, conflict_file in enumerate(conflicts, 1):
        file_path = conflict_file['file_path']
        relative_path = os.path.relpath(file_path, codebase_path)
        print(f"\n[{idx}/{len(conflicts)}] {relative_path}")

        for conflict_idx, conflict_section in enumerate(conflict_file['conflicts'], 1):
            translated_version = conflict_section['current']  # Current = target language
            english_version = conflict_section['incoming']  # Incoming = English

            print(f"  Conflict {conflict_idx}/{len(conflict_file['conflicts'])}: ", end='')

            # Ask OpenAI to check if translations are close enough
            should_keep_translated = translation_checker.check_translation_closeness(
                openai_client, english_version, translated_version
            )

            if should_keep_translated:
                print(f"Keeping {lang_name} (close enough)")
                conflict_section['resolution'] = translated_version
            else:
                print("Translating...", end=' ')
                new_translation = openai_client.translate(english_version)

                if new_translation:
                    print("Done")
                    conflict_section['resolution'] = new_translation
                else:
                    print("Failed - keeping for manual review")
                    conflict_section['resolution'] = None

    # Step 3: Apply resolutions
    print("\n" + "=" * 60)
    if args.dry_run:
        print("DRY RUN - Skipping file modifications")
    else:
        print("Applying resolutions...")
    print("=" * 60)

    files_modified = 0
    files_with_unresolved = 0
    total_resolved = 0
    total_unresolved = 0

    for conflict_file in conflicts:
        file_path = conflict_file['file_path']
        relative_path = os.path.relpath(file_path, codebase_path)
        resolved_count = sum(1 for c in conflict_file['conflicts'] if c.get('resolution') is not None)
        unresolved_count = len(conflict_file['conflicts']) - resolved_count

        total_resolved += resolved_count
        total_unresolved += unresolved_count

        if resolved_count > 0 and not args.dry_run:
            if file_processor.resolve_conflicts_in_file(file_path, conflict_file):
                print(f"  {relative_path}: Resolved {resolved_count} conflict(s)")
                files_modified += 1
        elif resolved_count > 0:
            print(f"  {relative_path}: Would resolve {resolved_count} conflict(s)")

        if unresolved_count > 0:
            files_with_unresolved += 1
            print(f"  {relative_path}: {unresolved_count} conflict(s) need manual review")

    # Step 4: Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Target language:         {lang_name} ({lang_code})")
    print(f"Total files processed:   {len(conflicts)}")
    print(f"Total conflicts found:   {total_resolved + total_unresolved}")
    print(f"  Resolved automatically: {total_resolved}")
    print(f"  Need manual review:     {total_unresolved}")

    if not args.dry_run:
        print(f"\nFiles modified: {files_modified}")

    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)

    if args.dry_run:
        print("  1. Review the analysis above")
        print("  2. Run without --dry-run to apply changes")
    elif files_with_unresolved > 0:
        print("  1. Review and manually resolve remaining conflicts:")
        print(f"     git diff --check  # to find remaining conflicts")
        print("  2. Test the changes thoroughly")
        print("  3. Stage and commit the resolved conflicts:")
        print("     git add .")
        print("     git commit -m 'Resolve merge conflicts with translation'")
    else:
        print("  1. Review all changes:")
        print("     git diff")
        print("  2. Test the changes thoroughly")
        print("  3. Stage and commit the changes:")
        print("     git add .")
        print("     git commit -m 'Resolve merge conflicts with translation'")

    return 0


if __name__ == "__main__":
    sys.exit(main())
