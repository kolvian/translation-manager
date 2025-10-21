# filepath: /translation-manager/translation-manager/config/rules.py

# Rules and constants for translation management

# Language preservation rules
LANGUAGE_PRESERVATION_RULES = {
    'english': {
        'preserve_code': True,
        'preserve_comments': True,
        'preserve_strings': True,
    },
    'french': {
        'preserve_code': True,
        'preserve_comments': True,
        'preserve_strings': True,
    }
}

# Translation closeness threshold
CLOSENESS_THRESHOLD = 0.8  # 80% similarity required for translations to be considered close enough

# OpenAI API settings
OPENAI_API_SETTINGS = {
    'model': 'gpt-3.5-turbo',
    'max_tokens': 150,
    'temperature': 0.7,
}

# Merge conflict detection rules
MERGE_CONFLICT_RULES = {
    'detect_conflicts': True,
    'conflict_markers': ['<<<<<<', '======', '>>>>>>'],
}