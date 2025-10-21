import unittest
from translation_checker import TranslationChecker

class TestTranslationChecker(unittest.TestCase):

    def setUp(self):
        self.translation_checker = TranslationChecker()

    def test_check_translation_closeness(self):
        # Test cases for checking translation closeness
        english_text = "Hello, how are you?"
        french_text_close = "Bonjour, comment ça va?"
        french_text_far = "Salut, quel temps fait-il?"

        self.assertTrue(self.translation_checker.check_translation_closeness(english_text, french_text_close))
        self.assertFalse(self.translation_checker.check_translation_closeness(english_text, french_text_far))

    def test_handle_translation(self):
        # Test cases for handling translations
        english_text = "Good morning"
        expected_french_translation = "Bonjour"

        translated_text = self.translation_checker.handle_translation(english_text)
        self.assertEqual(translated_text, expected_french_translation)

if __name__ == '__main__':
    unittest.main()