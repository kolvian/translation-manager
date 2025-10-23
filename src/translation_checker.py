class TranslationChecker:
    def __init__(self):
        pass

    def check_translation_closeness(self, openai_client, english_text, french_text):
        """Check if English and French versions are close enough to keep the French version."""
        return openai_client.check_translation_closeness(english_text, french_text)