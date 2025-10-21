import unittest
from src.openai_client import OpenAIClient

class TestOpenAIClient(unittest.TestCase):
    def setUp(self):
        self.client = OpenAIClient()

    def test_call_openai_api_success(self):
        response = self.client.call_openai_api("Translate 'Hello' to French")
        self.assertIn('translated_text', response)

    def test_call_openai_api_failure(self):
        with self.assertRaises(Exception):
            self.client.call_openai_api("Invalid request")

    def test_handle_response(self):
        mock_response = {
            'choices': [{'text': 'Bonjour'}],
            'status': 'success'
        }
        translated_text = self.client.handle_response(mock_response)
        self.assertEqual(translated_text, 'Bonjour')

    def test_handle_response_no_choices(self):
        mock_response = {
            'choices': [],
            'status': 'success'
        }
        translated_text = self.client.handle_response(mock_response)
        self.assertIsNone(translated_text)

if __name__ == '__main__':
    unittest.main()