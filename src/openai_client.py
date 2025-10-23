from openai import OpenAI
import json
import time

class OpenAIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        self.last_request_time = 0
        self.min_request_interval = 0.15  # 150ms between requests = ~400 RPM max (safely under 500 RPM limit)

    def _rate_limit(self):
        """Ensure we don't exceed rate limits by adding a small delay between requests."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        self.last_request_time = time.time()

    def check_translation_closeness(self, english_text, french_text):
        """Ask OpenAI if the English and French versions are close enough in meaning."""
        prompt = f"""You are a translation expert. Compare these two texts:

ENGLISH (incoming):
{english_text}

FRENCH (current):
{french_text}

Determine if the French text is an acceptable translation of the English text. 
Consider them "close enough" if they convey the same core meaning, even if the wording differs slightly.

Respond with ONLY a JSON object in this format:
{{"close_enough": true/false, "reasoning": "brief explanation"}}

Do not include any other text in your response."""

        try:
            self._rate_limit()
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": "You are a translation comparison expert. You only respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            content = response.choices[0].message.content.strip()

            # Try to parse the JSON response
            result = json.loads(content)
            return result.get('close_enough', False)

        except json.JSONDecodeError as e:
            print(f"    ⚠️  Error parsing JSON response: {e}")
            return False
        except Exception as e:
            error_msg = str(e)
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                print(f"    ⚠️  Rate limit hit - waiting 10 seconds...")
                time.sleep(10)
                return False
            elif "quota" in error_msg.lower():
                print(f"    ⚠️  API quota exceeded: {e}")
                return False
            else:
                print(f"    ⚠️  Error checking translation closeness: {e}")
                return False

    def translate_to_french(self, english_text):
        """Translate English text to French, being careful to preserve code blocks."""
        prompt = f"""Translate the following English text to French.

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
            self._rate_limit()
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": "You are a professional technical translator from English to French. You preserve code and technical terms."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            translated = response.choices[0].message.content.strip()

            # Check if translation failed
            if "TRANSLATION_FAILED" in translated or "TRADUCTION_ÉCHOUÉE" in translated:
                print(f"    ⚠️  Translation marked as failed by GPT")
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
            # Look for markers like "CRITICAL RULES", "RÈGLES", "Note:", etc.
            separators = [
                '\n\nCRITICAL RULES',
                '\n\nRÈGLES CRITIQUES',
                '\n\nNote:',
                '\n\nExplanation:',
                '\n\n---',
                '\n\n***',
            ]
            for separator in separators:
                if separator in translated:
                    translated = translated.split(separator)[0].strip()
                    break

            # Basic validation: make sure it's not still in English
            # (This is a simple heuristic - you might want to improve this)
            if self._appears_to_be_french(translated):
                return translated
            else:
                # Debug: show what was rejected
                preview = translated[:150] + '...' if len(translated) > 150 else translated
                print(f"    ⚠️  Translation appears to still be in English")
                print(f"        Preview: {repr(preview)}")
                return None

        except Exception as e:
            error_msg = str(e)
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                print(f"    ⚠️  Rate limit hit - waiting 10 seconds...")
                time.sleep(10)
                return None
            elif "quota" in error_msg.lower() or "insufficient_quota" in error_msg:
                print(f"    ⚠️  API quota exceeded: {e}")
                return None
            else:
                print(f"    ⚠️  Error translating text: {e}")
                return None
    
    def _appears_to_be_french(self, text):
        """Simple heuristic to check if text appears to be in French.

        For code blocks, we focus on string literals rather than code keywords.
        """
        import re

        text_lower = text.lower()

        # Check for French characters (accented characters)
        french_chars = ['é', 'è', 'ê', 'à', 'ù', 'ô', 'î', 'ç', 'â', 'û', 'ë', 'ï', 'ü', 'æ', 'œ']
        has_french_chars = any(char in text for char in french_chars)

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
                # Check if the string literals are in French
                combined_strings = ' '.join(string_literals)
                # If string literals have French chars, consider it French
                if any(char in combined_strings for char in french_chars):
                    return True

                # Check for French words in the strings
                french_words_in_strings = [
                    'histoire', 'l\'', 'd\'', 'de ', 'le ', 'la ', 'les ',
                    'composant', 'serveur', 'action', 'référence', 'guide'
                ]
                if any(word in combined_strings.lower() for word in french_words_in_strings):
                    return True

                # Check if there are any obvious English-only words in the strings
                combined_strings_lower = ' '.join(string_literals).lower()
                english_only_in_strings = ['story', 'component', 'server', 'action', 'reference']
                if any(word in combined_strings_lower for word in english_only_in_strings):
                    return False

            # Check comments for French
            if comment_text:
                if any(char in comment_text for char in french_chars):
                    return True

            # If it's code with no strings or only code keywords, accept it as valid
            # (Code keywords like const, function, etc. don't need translation)
            # This prevents false negatives for pure code blocks
            if not string_literals or len(' '.join(string_literals).strip()) < 5:
                # No meaningful strings to translate, code structure is fine
                return True

        # For non-code or when we can't determine from strings alone
        # Check for common French words (expanded list with more coverage)
        french_words = [
            ' le ', ' la ', ' les ', ' un ', ' une ', ' des ',
            ' pour ', ' dans ', ' sur ', ' avec ', ' sans ',
            ' est ', ' sont ', ' et ', ' de ', ' du ', ' à ', ' au ', ' aux ',
            ' qui ', ' que ', ' dont ', ' où ',
            ' cette ', ' ces ', ' ce ', ' cet ',
            ' vous ', ' nous ', ' ils ', ' elles ',
            ' être ', ' avoir ', ' faire ',
            ' peut ', ' pouvez ', ' peuvent ',
            ' voir ', ' utiliser ', ' créer ',
            'composants', 'composant', 'serveur',
            'nouveau', 'nouvelle', 'nouveaux', 'nouvelles',
            'histoire'
        ]
        text_with_spaces = ' ' + text_lower + ' '
        french_word_count = sum(1 for word in french_words if word in text_with_spaces)

        # Check for common English-only indicators
        english_indicators = [
            ' the ', ' for ', ' and ', ' of ', ' in ', ' to ', ' is ', ' are ',
            ' with ', ' from ', ' that ', ' this ', ' was ', ' will ', ' can '
        ]
        english_word_count = sum(1 for word in english_indicators if word in text_with_spaces)

        # Decision logic:
        # 1. If it has French accented characters, it's very likely French
        if has_french_chars:
            return True

        # 2. If it has strong English indicators and no French words, it's English
        if english_word_count > 0 and french_word_count == 0:
            return False

        # 3. For very short text (< 20 chars), require at least 1 French word
        if len(text.strip()) < 20:
            return french_word_count >= 1

        # 4. For short text (< 50 chars), require at least 1 French word
        if len(text.strip()) < 50:
            return french_word_count >= 1

        # 5. For longer text, require at least 2 French words
        # AND have more French indicators than English
        return french_word_count >= 2 and french_word_count > english_word_count