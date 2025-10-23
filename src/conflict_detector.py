import os

class ConflictDetector:
    def __init__(self, codebase):
        self.codebase = codebase

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
        
        Returns a list of dictionaries with 'current' (French) and 'incoming' (English) sections.
        """
        sections = []
        lines = content.splitlines()
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            if line.startswith('<<<<<<<'):
                # Start of conflict - current version (French)
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
                    'current': '\n'.join(current_lines),  # French version
                    'incoming': '\n'.join(incoming_lines),  # English version
                    'start_line': i - len(current_lines) - len(incoming_lines) - 2,
                    'end_line': i
                })
            
            i += 1
        
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