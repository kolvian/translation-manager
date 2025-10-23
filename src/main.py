import os
import sys
import argparse
from dotenv import load_dotenv
from conflict_detector import ConflictDetector
from translation_checker import TranslationChecker
from openai_client import OpenAIClient
from file_processor import FileProcessor

def parse_args():
    parser = argparse.ArgumentParser(
        description='Automatically resolve merge conflicts by translating English to French using OpenAI.'
    )
    parser.add_argument(
        '--codebase-path',
        type=str,
        help='Path to the codebase to scan for conflicts (default: ../fr.react.dev)'
    )
    parser.add_argument(
        '--env-file',
        type=str,
        help='Path to .env.local file with OPENAI_API_KEY (default: ../fr.react.dev/.env.local)'
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

def main():
    args = parse_args()
    
    # Load environment variables from .env.local
    if args.env_file:
        env_path = args.env_file
    else:
        env_path = os.path.join(os.path.dirname(__file__), '..', '..', 'fr.react.dev', '.env.local')
    
    load_dotenv(env_path)
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if not openai_api_key:
        print(f"Error: OPENAI_API_KEY not found in {env_path}")
        print("Please set the API key in the .env.local file")
        return 1
    
    # Get the codebase path
    if args.codebase_path:
        codebase_path = args.codebase_path
    else:
        codebase_path = os.path.join(os.path.dirname(__file__), '..', '..', 'fr.react.dev')
    
    codebase_path = os.path.abspath(codebase_path)
    
    if not os.path.exists(codebase_path):
        print(f"Error: Codebase path does not exist: {codebase_path}")
        return 1
    
    print(f"Scanning codebase: {codebase_path}")
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
    print()

    # Initialize components
    conflict_detector = ConflictDetector(codebase_path)
    translation_checker = TranslationChecker()
    openai_client = OpenAIClient(openai_api_key)
    file_processor = FileProcessor()

    # Step 1: Detect merge conflicts
    conflicts = conflict_detector.find_merge_conflicts()
    
    if not conflicts:
        print("✓ No merge conflicts found in the codebase.")
        return 0
    
    # Limit files if requested
    if args.max_files and len(conflicts) > args.max_files:
        print(f"⚠️  Limiting to first {args.max_files} files (found {len(conflicts)} total)")
        conflicts = conflicts[:args.max_files]
    
    print(f"Found {len(conflicts)} file(s) with merge conflicts.\n")

    # Step 2: Check translation closeness and manage translations
    print("Analyzing conflicts with OpenAI...")
    print("="*60)
    
    for idx, conflict_file in enumerate(conflicts, 1):
        file_path = conflict_file['file_path']
        relative_path = os.path.relpath(file_path, codebase_path)
        print(f"\n[{idx}/{len(conflicts)}] {relative_path}")
        
        for conflict_idx, conflict_section in enumerate(conflict_file['conflicts'], 1):
            french_version = conflict_section['current']  # Current = French
            english_version = conflict_section['incoming']  # Incoming = English
            
            print(f"  Conflict {conflict_idx}/{len(conflict_file['conflicts'])}: ", end='')
            
            # Ask OpenAI to check if translations are close enough
            should_keep_french = translation_checker.check_translation_closeness(
                openai_client, english_version, french_version
            )
            
            if should_keep_french:
                print("✓ Keeping French (close enough)")
                conflict_section['resolution'] = french_version
            else:
                print("🔄 Translating...", end=' ')
                translated_text = openai_client.translate_to_french(english_version)
                
                if translated_text:
                    print("✓ Done")
                    conflict_section['resolution'] = translated_text
                else:
                    print("⚠️  Failed - keeping for manual review")
                    conflict_section['resolution'] = None
    
    # Step 3: Apply resolutions
    print("\n" + "="*60)
    if args.dry_run:
        print("DRY RUN - Skipping file modifications")
    else:
        print("Applying resolutions...")
    print("="*60)
    
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
                print(f"✓ {relative_path}: Resolved {resolved_count} conflict(s)")
                files_modified += 1
        elif resolved_count > 0:
            print(f"🔍 {relative_path}: Would resolve {resolved_count} conflict(s)")
        
        if unresolved_count > 0:
            files_with_unresolved += 1
            print(f"⚠️  {relative_path}: {unresolved_count} conflict(s) need manual review")
    
    # Step 4: Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total files processed: {len(conflicts)}")
    print(f"Total conflicts found: {total_resolved + total_unresolved}")
    print(f"  ✓ Resolved automatically: {total_resolved}")
    print(f"  ⚠️  Need manual review: {total_unresolved}")
    
    if not args.dry_run:
        print(f"\nFiles modified: {files_modified}")
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    
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