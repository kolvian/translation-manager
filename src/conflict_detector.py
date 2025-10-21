class ConflictDetector:
    def __init__(self, codebase):
        self.codebase = codebase

    def find_merge_conflicts(self):
        conflicts = []
        for file_path in self.codebase:
            with open(file_path, 'r') as file:
                content = file.read()
                if self._has_conflict(content):
                    conflicts.append(file_path)
        return conflicts

    def _has_conflict(self, content):
        # Simple heuristic to identify merge conflict markers
        return '<<<<<<<' in content and '>>>>>>>' in content

    def extract_conflict_sections(self, content):
        # Extract sections of the content that are in conflict
        sections = []
        lines = content.splitlines()
        in_conflict = False
        conflict_section = []

        for line in lines:
            if line.startswith('<<<<<<<'):
                in_conflict = True
                conflict_section = [line]
            elif line.startswith('>>>>>>>'):
                in_conflict = False
                conflict_section.append(line)
                sections.append('\n'.join(conflict_section))
            elif in_conflict:
                conflict_section.append(line)

        return sections

    def identify_languages(self, conflict_sections):
        language_info = []
        for section in conflict_sections:
            if self._is_english(section):
                language_info.append(('English', section))
            elif self._is_french(section):
                language_info.append(('French', section))
        return language_info

    def _is_english(self, text):
        # Basic check for English text (could be improved with NLP)
        return any(char.isascii() for char in text)

    def _is_french(self, text):
        # Basic check for French text (could be improved with NLP)
        french_keywords = ['le', 'la', 'et', 'à', 'de', 'un', 'une']
        return any(keyword in text for keyword in french_keywords)