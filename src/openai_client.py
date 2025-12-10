from openai import OpenAI
import json
import time
import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config.rules import SUPPORTED_LANGUAGES, ENGLISH_INDICATORS, get_language_config


class OpenAIClient:
    def __init__(self, api_key, target_language='french'):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        self.set_target_language(target_language)

    def set_target_language(self, language):
        """Set the target language for translations."""
        lang_config = get_language_config(language)
        if not lang_config:
            raise ValueError(f"Unsupported language: {language}. Supported: {list(SUPPORTED_LANGUAGES.keys())}")
        self.target_language = language
        self.language_config = lang_config

    def check_translation_closeness(self, english_text, translated_text):
        """Ask OpenAI if the English and translated versions are close enough in meaning."""
        lang_name = self.language_config['name']

        prompt = f"""You are a translation expert. Compare these two texts:

ENGLISH (incoming):
{english_text}

{lang_name.upper()} (current):
{translated_text}

Determine if the {lang_name} text is an acceptable translation of the English text.
Consider them "close enough" if they convey the same core meaning, even if the wording differs slightly.

Respond with ONLY a JSON object in this format:
{{"close_enough": true/false, "reasoning": "brief explanation"}}

Do not include any other text in your response."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": "You are a translation comparison expert. You only respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1
            )

            content = response.choices[0].message.content.strip()

            # Try to parse the JSON response
            result = json.loads(content)
            return result.get('close_enough', False)

        except json.JSONDecodeError as e:
            print(f"    Warning: Error parsing JSON response: {e}")
            return False
        except Exception as e:
            error_msg = str(e)
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                print(f"    Warning: Rate limit hit - waiting 10 seconds...")
                time.sleep(10)
                return False
            elif "quota" in error_msg.lower():
                print(f"    Warning: API quota exceeded: {e}")
                return False
            else:
                print(f"    Warning: Error checking translation closeness: {e}")
                return False

    def translate(self, english_text):
        """Translate English text to the target language, being careful to preserve code blocks."""
        lang_name = self.language_config['name']

        prompt = f"""Translate the following English text to {lang_name}.

CRITICAL RULES:
1. ONLY translate natural language text (string values, comments, documentation)
2. DO NOT translate: code keywords, function names, variable names, technical identifiers
3. Keep all code structure, syntax, and formatting exactly as-is
4. If you cannot provide a proper translation, respond with exactly: TRANSLATION_FAILED
5. DO NOT add explanations, comments, or any extra text
6. Your response must contain ONLY the translated version, nothing else

Text to translate:
{english_text}

Translated version (NOTHING ELSE):"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": f"You are a professional technical translator from English to {lang_name}. You preserve code and technical terms."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1
            )

            translated = response.choices[0].message.content.strip()

            # Check if translation failed
            if "TRANSLATION_FAILED" in translated:
                print(f"    Warning: Translation marked as failed by GPT")
                return None

            # Clean up the response - sometimes GPT adds extra explanatory text
            # Look for common patterns where GPT adds extra content after the translation

            # Remove markdown code blocks if GPT wrapped the response
            if translated.startswith('```') and '\n```' in translated:
                # Extract content from code block
                start = translated.find('\n') + 1
                end = translated.rfind('\n```')
                if start > 0 and end > start:
                    translated = translated[start:end]

            # If GPT added explanatory text after the translation, try to extract just the translation
            # Look for markers like "CRITICAL RULES", "Note:", etc.
            separators = [
                '\n\nCRITICAL RULES',
                '\n\nNote:',
                '\n\nExplanation:',
                '\n\n---',
                '\n\n***',
            ]
            for separator in separators:
                if separator in translated:
                    translated = translated.split(separator)[0].strip()
                    break

            # Basic validation: make sure it's in the target language
            if self._appears_to_be_target_language(translated):
                return translated
            else:
                # Debug: show what was rejected
                preview = translated[:150] + '...' if len(translated) > 150 else translated
                print(f"    Warning: Translation appears to still be in English")
                print(f"        Preview: {repr(preview)}")
                return None

        except Exception as e:
            error_msg = str(e)
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                print(f"    Warning: Rate limit hit - waiting 10 seconds...")
                time.sleep(10)
                return None
            elif "quota" in error_msg.lower() or "insufficient_quota" in error_msg:
                print(f"    Warning: API quota exceeded: {e}")
                return None
            else:
                print(f"    Warning: Error translating text: {e}")
                return None

    def check_and_translate(self, english_text, existing_translation):
        """Check if existing translation is close enough, and translate if not - in a single API call.

        Returns a dict with:
            - 'close_enough': bool - whether the existing translation was acceptable
            - 'translation': str or None - the new translation if needed, None if existing was kept
        """
        lang_name = self.language_config['name']

        prompt = f"""You are a translation expert. Compare the English text with the existing {lang_name} translation.

ENGLISH TEXT:
{english_text}

EXISTING {lang_name.upper()} TRANSLATION:
{existing_translation}

Your task:
1. Determine if the existing {lang_name} translation is acceptable (conveys the same core meaning as the English)
2. If NOT acceptable, provide a new translation

CRITICAL TRANSLATION RULES (if you need to translate):
- ONLY translate natural language text (string values, comments, documentation)
- DO NOT translate: code keywords, function names, variable names, technical identifiers
- Keep all code structure, syntax, and formatting exactly as-is

Respond with ONLY a JSON object in this exact format:
{{"close_enough": true/false, "reasoning": "brief explanation", "new_translation": "the new translation if close_enough is false, otherwise null"}}

Do not include any other text in your response."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": f"You are a professional translator and translation evaluator for {lang_name}. You only respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1
            )

            content = response.choices[0].message.content.strip()
            result = json.loads(content)

            close_enough = result.get('close_enough', False)

            if close_enough:
                return {'close_enough': True, 'translation': None}

            new_translation = result.get('new_translation')

            if not new_translation or new_translation == 'null':
                # Fallback: translation was needed but not provided
                print(f"    Warning: Model indicated translation needed but didn't provide one")
                return {'close_enough': False, 'translation': None}

            # Validate the new translation
            if self._appears_to_be_target_language(new_translation):
                return {'close_enough': False, 'translation': new_translation}
            else:
                preview = new_translation[:100] + '...' if len(new_translation) > 100 else new_translation
                print(f"    Warning: New translation appears to still be in English")
                print(f"        Preview: {repr(preview)}")
                return {'close_enough': False, 'translation': None}

        except json.JSONDecodeError as e:
            print(f"    Warning: Error parsing JSON response: {e}")
            return {'close_enough': False, 'translation': None}
        except Exception as e:
            error_msg = str(e)
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                print(f"    Warning: Rate limit hit - waiting 10 seconds...")
                time.sleep(10)
                return {'close_enough': False, 'translation': None}
            elif "quota" in error_msg.lower() or "insufficient_quota" in error_msg:
                print(f"    Warning: API quota exceeded: {e}")
                return {'close_enough': False, 'translation': None}
            else:
                print(f"    Warning: Error in check_and_translate: {e}")
                return {'close_enough': False, 'translation': None}

    # Keep backwards compatibility
    def translate_to_french(self, english_text):
        """Deprecated: Use translate() instead. Kept for backwards compatibility."""
        old_lang = self.target_language
        self.set_target_language('french')
        result = self.translate(english_text)
        self.set_target_language(old_lang)
        return result

    def _appears_to_be_target_language(self, text):
        """Check if text appears to be in the target language.

        For code blocks, we focus on string literals rather than code keywords.
        """
        import re

        text_lower = text.lower()
        lang_config = self.language_config

        # Check for language-specific characters (accented characters)
        accented_chars = lang_config.get('accented_chars', [])
        has_lang_chars = any(char in text for char in accented_chars) if accented_chars else False

        # Check for character ranges (for CJK, Cyrillic, Arabic, etc.)
        char_ranges = lang_config.get('char_ranges', [])
        if char_ranges:
            for char in text:
                code_point = ord(char)
                for start, end in char_ranges:
                    if start <= code_point <= end:
                        has_lang_chars = True
                        break
                if has_lang_chars:
                    break

        # If this looks like code (has common code patterns), extract string literals
        code_indicators = ['const ', 'let ', 'var ', 'function ', 'class ', '{', '}', '(', ')', '=>', 'import ', 'export ']
        looks_like_code = any(indicator in text for indicator in code_indicators)

        if looks_like_code:
            # For code, extract string literals and check those specifically
            # Match strings in quotes (both single and double)
            string_literals = re.findall(r'["\']([^"\']+)["\']', text)

            # Also check for comments (// or /* */)
            comments = re.findall(r'//\s*(.+?)$|/\*\s*(.+?)\s*\*/', text, re.MULTILINE)
            comment_text = ' '.join([c[0] or c[1] for c in comments if c])

            if string_literals:
                # Check if the string literals are in the target language
                combined_strings = ' '.join(string_literals)

                # If string literals have target language chars, consider it translated
                if accented_chars and any(char in combined_strings for char in accented_chars):
                    return True

                # Check for character ranges in strings
                if char_ranges:
                    for char in combined_strings:
                        code_point = ord(char)
                        for start, end in char_ranges:
                            if start <= code_point <= end:
                                return True

                # Check for target language words in the strings
                string_indicators = lang_config.get('string_indicators', [])
                if any(word in combined_strings.lower() for word in string_indicators):
                    return True

                # Check if there are any obvious English-only words in the strings
                combined_strings_lower = ' '.join(string_literals).lower()
                english_only_in_strings = ['story', 'component', 'server', 'action', 'reference']
                if any(word in combined_strings_lower for word in english_only_in_strings):
                    return False

            # Check comments for target language
            if comment_text:
                if accented_chars and any(char in comment_text for char in accented_chars):
                    return True

            # If it's code with no strings or only code keywords, accept it as valid
            # (Code keywords like const, function, etc. don't need translation)
            if not string_literals or len(' '.join(string_literals).strip()) < 5:
                # No meaningful strings to translate, code structure is fine
                return True

        # For non-code or when we can't determine from strings alone
        # Check for common target language words
        common_words = lang_config.get('common_words', [])
        text_with_spaces = ' ' + text_lower + ' '
        lang_word_count = sum(1 for word in common_words if word in text_with_spaces)

        # Check for common English indicators
        english_word_count = sum(1 for word in ENGLISH_INDICATORS if word in text_with_spaces)

        # Decision logic:
        # 1. If it has target language characters, it's very likely in target language
        if has_lang_chars:
            return True

        # 2. If it has strong English indicators and no target language words, it's English
        if english_word_count > 0 and lang_word_count == 0:
            return False

        # 3. For very short text (< 20 chars), require at least 1 target language word
        if len(text.strip()) < 20:
            return lang_word_count >= 1

        # 4. For short text (< 50 chars), require at least 1 target language word
        if len(text.strip()) < 50:
            return lang_word_count >= 1

        # 5. For longer text, require at least 2 target language words
        # AND have more target language indicators than English
        return lang_word_count >= 2 and lang_word_count > english_word_count

    # Keep backwards compatibility
    def _appears_to_be_french(self, text):
        """Deprecated: Use _appears_to_be_target_language() instead."""
        old_lang = self.target_language
        self.set_target_language('french')
        result = self._appears_to_be_target_language(text)
        self.set_target_language(old_lang)
        return result
