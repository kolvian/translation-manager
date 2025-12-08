import os
import sys

# Add parent directory to path to import config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config.rules import SUPPORTED_LANGUAGES, ENGLISH_INDICATORS, get_language_config


class ConflictDetector:
    def __init__(self, codebase, target_language='french'):
        self.codebase = codebase
        self.set_target_language(target_language)

    def set_target_language(self, language):
        """Set the target language for conflict detection."""
        lang_config = get_language_config(language)
        if not lang_config:
            raise ValueError(f"Unsupported language: {language}. Supported: {list(SUPPORTED_LANGUAGES.keys())}")
        self.target_language = language
        self.language_config = lang_config

    def find_merge_conflicts(self):
        """Find all files with merge conflicts in the codebase."""
        conflicts = []

        # Walk through all files in the codebase directory
        for root, dirs, files in os.walk(self.codebase):
            # Skip common directories that don't need translation
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '.venv', '__pycache__', 'build', 'dist']]

            for file in files:
                file_path = os.path.join(root, file)

                # Only process text files (skip binary files)
                if self._is_text_file(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if self._has_conflict(content):
                                conflict_sections = self.extract_conflict_sections(content)
                                conflicts.append({
                                    'file_path': file_path,
                                    'content': content,
                                    'conflicts': conflict_sections
                                })
                    except (UnicodeDecodeError, PermissionError):
                        # Skip files that can't be read as text
                        continue

        return conflicts

    def _is_text_file(self, file_path):
        """Check if a file is likely a text file based on extension."""
        text_extensions = [
            '.md', '.mdx', '.txt', '.js', '.jsx', '.ts', '.tsx',
            '.json', '.html', '.css', '.scss', '.yml', '.yaml',
            '.py', '.java', '.c', '.cpp', '.h', '.xml'
        ]
        return any(file_path.endswith(ext) for ext in text_extensions)

    def _has_conflict(self, content):
        """Check if content has merge conflict markers."""
        return '<<<<<<< HEAD' in content or '<<<<<<<' in content

    def extract_conflict_sections(self, content):
        """Extract sections of content that are in conflict.

        Returns a list of dictionaries with 'current' (target language) and 'incoming' (English) sections.
        """
        sections = []
        lines = content.splitlines()
        i = 0

        while i < len(lines):
            line = lines[i]

            if line.startswith('<<<<<<<'):
                # Start of conflict - current version (target language)
                current_lines = []
                i += 1

                # Collect current version lines until we hit the separator
                while i < len(lines) and not lines[i].startswith('======='):
                    current_lines.append(lines[i])
                    i += 1

                # Skip the separator
                if i < len(lines):
                    i += 1

                # Collect incoming version lines (English) until we hit the end marker
                incoming_lines = []
                while i < len(lines) and not lines[i].startswith('>>>>>>>'):
                    incoming_lines.append(lines[i])
                    i += 1

                sections.append({
                    'current': '\n'.join(current_lines),  # Target language version
                    'incoming': '\n'.join(incoming_lines),  # English version
                    'start_line': i - len(current_lines) - len(incoming_lines) - 2,
                    'end_line': i
                })

            i += 1

        return sections

    def identify_languages(self, conflict_sections):
        """Identify the language of each conflict section."""
        language_info = []
        for section in conflict_sections:
            if self._is_english(section):
                language_info.append(('English', section))
            elif self._is_target_language(section):
                language_info.append((self.language_config['name'], section))
        return language_info

    def _is_english(self, text):
        """Check if text appears to be in English."""
        text_lower = ' ' + text.lower() + ' '
        english_count = sum(1 for word in ENGLISH_INDICATORS if word in text_lower)
        return english_count > 0

    def _is_target_language(self, text):
        """Check if text appears to be in the target language."""
        lang_config = self.language_config
        text_lower = text.lower()

        # Check for accented characters
        accented_chars = lang_config.get('accented_chars', [])
        if accented_chars and any(char in text for char in accented_chars):
            return True

        # Check for character ranges (for CJK, Cyrillic, Arabic, etc.)
        char_ranges = lang_config.get('char_ranges', [])
        if char_ranges:
            for char in text:
                code_point = ord(char)
                for start, end in char_ranges:
                    if start <= code_point <= end:
                        return True

        # Check for common keywords
        keywords = lang_config.get('keywords', [])
        return any(keyword in text_lower for keyword in keywords)

    # Keep backwards compatibility
    def _is_french(self, text):
        """Deprecated: Use _is_target_language() instead."""
        old_lang = self.target_language
        self.set_target_language('french')
        result = self._is_target_language(text)
        self.set_target_language(old_lang)
        return result
