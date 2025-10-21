import os
from dotenv import load_dotenv
from conflict_detector import ConflictDetector
from translation_checker import TranslationChecker
from openai_client import OpenAIClient

def main():
    # Load environment variables
    load_dotenv()
    openai_api_key = os.getenv('OPENAI_API_KEY')

    # Initialize components
    conflict_detector = ConflictDetector()
    translation_checker = TranslationChecker()
    openai_client = OpenAIClient(openai_api_key)

    # Step 1: Detect merge conflicts
    conflicts = conflict_detector.find_merge_conflicts()

    # Step 2: Check translation closeness and manage translations
    for conflict in conflicts:
        english_version = conflict['english']
        french_version = conflict['french']

        if translation_checker.check_translation_closeness(english_version, french_version):
            print("Translations are close enough, no action needed.")
        else:
            translated_text = openai_client.call_openai_api(english_version)
            translation_checker.handle_translation(conflict, translated_text)

if __name__ == "__main__":
    main()