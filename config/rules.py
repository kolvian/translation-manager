# filepath: /translation-manager/translation-manager/config/rules.py

# Rules and constants for translation management

# Supported languages with their detection heuristics
SUPPORTED_LANGUAGES = {
    'french': {
        'code': 'fr',
        'name': 'French',
        'native_name': 'Français',
        'accented_chars': ['é', 'è', 'ê', 'à', 'ù', 'ô', 'î', 'ç', 'â', 'û', 'ë', 'ï', 'ü', 'æ', 'œ'],
        'common_words': [
            ' le ', ' la ', ' les ', ' un ', ' une ', ' des ',
            ' pour ', ' dans ', ' sur ', ' avec ', ' sans ',
            ' est ', ' sont ', ' et ', ' de ', ' du ', ' à ', ' au ', ' aux ',
            ' qui ', ' que ', ' dont ', ' où ',
            ' cette ', ' ces ', ' ce ', ' cet ',
            ' vous ', ' nous ', ' ils ', ' elles ',
            ' être ', ' avoir ', ' faire ',
            ' peut ', ' pouvez ', ' peuvent ',
            ' voir ', ' utiliser ', ' créer ',
        ],
        'string_indicators': [
            'histoire', "l'", "d'", 'de ', 'le ', 'la ', 'les ',
            'composant', 'serveur', 'action', 'référence', 'guide'
        ],
        'keywords': ['le', 'la', 'et', 'à', 'de', 'un', 'une'],
    },
    'spanish': {
        'code': 'es',
        'name': 'Spanish',
        'native_name': 'Español',
        'accented_chars': ['á', 'é', 'í', 'ó', 'ú', 'ü', 'ñ', '¿', '¡'],
        'common_words': [
            ' el ', ' la ', ' los ', ' las ', ' un ', ' una ', ' unos ', ' unas ',
            ' para ', ' en ', ' con ', ' sin ', ' sobre ',
            ' es ', ' son ', ' y ', ' de ', ' del ', ' a ', ' al ',
            ' que ', ' como ', ' cuando ', ' donde ',
            ' esta ', ' este ', ' estos ', ' estas ',
            ' usted ', ' nosotros ', ' ellos ', ' ellas ',
            ' ser ', ' estar ', ' tener ', ' hacer ',
            ' puede ', ' pueden ',
        ],
        'string_indicators': [
            'historia', 'componente', 'servidor', 'acción', 'referencia', 'guía'
        ],
        'keywords': ['el', 'la', 'y', 'de', 'un', 'una', 'que'],
    },
    'german': {
        'code': 'de',
        'name': 'German',
        'native_name': 'Deutsch',
        'accented_chars': ['ä', 'ö', 'ü', 'ß'],
        'common_words': [
            ' der ', ' die ', ' das ', ' ein ', ' eine ', ' eines ',
            ' für ', ' in ', ' mit ', ' ohne ', ' auf ', ' über ',
            ' ist ', ' sind ', ' und ', ' von ', ' zu ', ' an ',
            ' was ', ' wie ', ' wann ', ' wo ',
            ' diese ', ' dieser ', ' dieses ',
            ' Sie ', ' wir ', ' sie ',
            ' sein ', ' haben ', ' machen ', ' werden ',
            ' kann ', ' können ',
        ],
        'string_indicators': [
            'Geschichte', 'Komponente', 'Server', 'Aktion', 'Referenz', 'Anleitung'
        ],
        'keywords': ['der', 'die', 'das', 'und', 'von', 'ein', 'eine'],
    },
    'portuguese': {
        'code': 'pt',
        'name': 'Portuguese',
        'native_name': 'Português',
        'accented_chars': ['á', 'à', 'â', 'ã', 'é', 'ê', 'í', 'ó', 'ô', 'õ', 'ú', 'ç'],
        'common_words': [
            ' o ', ' a ', ' os ', ' as ', ' um ', ' uma ', ' uns ', ' umas ',
            ' para ', ' em ', ' com ', ' sem ', ' sobre ',
            ' é ', ' são ', ' e ', ' de ', ' do ', ' da ', ' ao ', ' à ',
            ' que ', ' como ', ' quando ', ' onde ',
            ' este ', ' esta ', ' estes ', ' estas ',
            ' você ', ' nós ', ' eles ', ' elas ',
            ' ser ', ' estar ', ' ter ', ' fazer ',
            ' pode ', ' podem ',
        ],
        'string_indicators': [
            'história', 'componente', 'servidor', 'ação', 'referência', 'guia'
        ],
        'keywords': ['o', 'a', 'e', 'de', 'um', 'uma', 'que'],
    },
    'italian': {
        'code': 'it',
        'name': 'Italian',
        'native_name': 'Italiano',
        'accented_chars': ['à', 'è', 'é', 'ì', 'ò', 'ù'],
        'common_words': [
            ' il ', ' lo ', ' la ', ' i ', ' gli ', ' le ', ' un ', ' una ',
            ' per ', ' in ', ' con ', ' senza ', ' su ',
            ' è ', ' sono ', ' e ', ' di ', ' del ', ' della ', ' a ', ' al ', ' alla ',
            ' che ', ' come ', ' quando ', ' dove ',
            ' questo ', ' questa ', ' questi ', ' queste ',
            ' voi ', ' noi ', ' loro ',
            ' essere ', ' avere ', ' fare ',
            ' può ', ' possono ',
        ],
        'string_indicators': [
            'storia', 'componente', 'server', 'azione', 'riferimento', 'guida'
        ],
        'keywords': ['il', 'la', 'e', 'di', 'un', 'una', 'che'],
    },
    'japanese': {
        'code': 'ja',
        'name': 'Japanese',
        'native_name': '日本語',
        'accented_chars': [],  # Japanese uses different character sets
        'char_ranges': [(0x3040, 0x309F), (0x30A0, 0x30FF), (0x4E00, 0x9FFF)],  # Hiragana, Katakana, Kanji
        'common_words': ['の', 'は', 'が', 'を', 'に', 'で', 'と', 'も', 'から', 'まで'],
        'string_indicators': ['コンポーネント', 'サーバー', 'アクション', 'ガイド'],
        'keywords': ['の', 'は', 'が', 'を', 'に'],
    },
    'chinese': {
        'code': 'zh',
        'name': 'Chinese',
        'native_name': '中文',
        'accented_chars': [],
        'char_ranges': [(0x4E00, 0x9FFF), (0x3400, 0x4DBF)],  # CJK Unified Ideographs
        'common_words': ['的', '是', '在', '有', '和', '了', '不', '这', '那', '我', '你', '他'],
        'string_indicators': ['组件', '服务器', '操作', '指南'],
        'keywords': ['的', '是', '在', '有', '和'],
    },
    'korean': {
        'code': 'ko',
        'name': 'Korean',
        'native_name': '한국어',
        'accented_chars': [],
        'char_ranges': [(0xAC00, 0xD7AF), (0x1100, 0x11FF)],  # Hangul Syllables, Jamo
        'common_words': ['의', '은', '는', '이', '가', '을', '를', '에', '에서', '와', '과'],
        'string_indicators': ['컴포넌트', '서버', '액션', '가이드'],
        'keywords': ['의', '은', '는', '이', '가'],
    },
    'russian': {
        'code': 'ru',
        'name': 'Russian',
        'native_name': 'Русский',
        'accented_chars': [],
        'char_ranges': [(0x0400, 0x04FF)],  # Cyrillic
        'common_words': [' в ', ' на ', ' с ', ' и ', ' не ', ' что ', ' это ', ' как ', ' для ', ' по '],
        'string_indicators': ['компонент', 'сервер', 'действие', 'руководство'],
        'keywords': ['в', 'на', 'и', 'не', 'что', 'это'],
    },
    'arabic': {
        'code': 'ar',
        'name': 'Arabic',
        'native_name': 'العربية',
        'accented_chars': [],
        'char_ranges': [(0x0600, 0x06FF), (0x0750, 0x077F)],  # Arabic
        'common_words': ['في', 'من', 'على', 'إلى', 'أن', 'هذا', 'مع', 'هو', 'هي'],
        'string_indicators': ['مكون', 'خادم', 'إجراء', 'دليل'],
        'keywords': ['في', 'من', 'على', 'إلى', 'أن'],
    },
    'dutch': {
        'code': 'nl',
        'name': 'Dutch',
        'native_name': 'Nederlands',
        'accented_chars': ['é', 'ë', 'ï', 'ö', 'ü'],
        'common_words': [
            ' de ', ' het ', ' een ', ' van ', ' en ', ' in ', ' op ', ' met ',
            ' is ', ' zijn ', ' voor ', ' aan ', ' naar ', ' door ',
            ' die ', ' dat ', ' wat ', ' wie ', ' waar ',
        ],
        'string_indicators': ['verhaal', 'component', 'server', 'actie', 'gids'],
        'keywords': ['de', 'het', 'een', 'en', 'van', 'in'],
    },
    'polish': {
        'code': 'pl',
        'name': 'Polish',
        'native_name': 'Polski',
        'accented_chars': ['ą', 'ć', 'ę', 'ł', 'ń', 'ó', 'ś', 'ź', 'ż'],
        'common_words': [
            ' i ', ' w ', ' na ', ' z ', ' do ', ' nie ', ' to ', ' jest ',
            ' się ', ' że ', ' o ', ' jak ', ' ale ', ' po ',
        ],
        'string_indicators': ['historia', 'komponent', 'serwer', 'akcja', 'przewodnik'],
        'keywords': ['i', 'w', 'na', 'z', 'do', 'nie', 'to'],
    },
}

# English detection (source language)
ENGLISH_INDICATORS = [
    ' the ', ' for ', ' and ', ' of ', ' in ', ' to ', ' is ', ' are ',
    ' with ', ' from ', ' that ', ' this ', ' was ', ' will ', ' can ',
    ' you ', ' we ', ' they ', ' have ', ' has ', ' been ', ' were ',
]

# Language preservation rules
LANGUAGE_PRESERVATION_RULES = {
    'english': {
        'preserve_code': True,
        'preserve_comments': True,
        'preserve_strings': True,
    },
}

# Add preservation rules for all supported languages
for lang_key in SUPPORTED_LANGUAGES:
    LANGUAGE_PRESERVATION_RULES[lang_key] = {
        'preserve_code': True,
        'preserve_comments': True,
        'preserve_strings': True,
    }

# Translation closeness threshold
CLOSENESS_THRESHOLD = 0.8  # 80% similarity required for translations to be considered close enough

# OpenAI API settings
OPENAI_API_SETTINGS = {
    'model': 'gpt-5-mini',
    'max_tokens': 150,
    'temperature': 0.7,
}

# Merge conflict detection rules
MERGE_CONFLICT_RULES = {
    'detect_conflicts': True,
    'conflict_markers': ['<<<<<<', '======', '>>>>>>'],
}

# Default configuration
DEFAULT_CONFIG = {
    'target_language': 'french',
    'source_language': 'english',
    'codebase_path': None,  # Must be specified
    'env_file': None,  # Will look for .env.local in codebase if not specified
}


def get_language_config(language_code):
    """Get the configuration for a language by its code or name."""
    # Check by key first
    if language_code.lower() in SUPPORTED_LANGUAGES:
        return SUPPORTED_LANGUAGES[language_code.lower()]

    # Check by language code (e.g., 'fr', 'es')
    for key, config in SUPPORTED_LANGUAGES.items():
        if config['code'] == language_code.lower():
            return config

    return None


def list_supported_languages():
    """Return a formatted list of supported languages."""
    return [(key, config['name'], config['code']) for key, config in SUPPORTED_LANGUAGES.items()]
