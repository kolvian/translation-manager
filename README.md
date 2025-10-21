# Translation Manager

Translation Manager is a Python application designed to identify merge conflicts in a codebase, check the closeness of English and French translations, and manage translations using the OpenAI API. This project aims to streamline the process of handling multilingual codebases while preserving the integrity of the original code.

## Features

- **Merge Conflict Detection**: Scans the codebase for merge conflicts, identifying sections with incoming changes in English and original changes in French.
- **Translation Closeness Checking**: Evaluates the similarity between English and French versions to determine if they are close enough for translation.
- **OpenAI API Integration**: Utilizes the OpenAI API for managing translations, ensuring that the output adheres to specific language preservation rules.
- **File Processing**: Handles reading and writing files, ensuring that code remains unchanged during the merge conflict resolution process.

## Project Structure

```
translation-manager
├── src
│   ├── main.py                # Entry point of the application
│   ├── conflict_detector.py    # Contains ConflictDetector class for merge conflict detection
│   ├── translation_checker.py   # Contains TranslationChecker class for translation management
│   ├── openai_client.py        # Contains OpenAIClient class for API interaction
│   ├── file_processor.py       # Functions for file operations
│   └── utils
│       ├── __init__.py        # Initializes the utils package
│       ├── file_utils.py      # Utility functions for file operations
│       └── diff_utils.py      # Utility functions for comparing text
├── config
│   ├── __init__.py            # Initializes the config package
│   └── rules.py               # Defines rules and constants for the project
├── tests
│   ├── __init__.py            # Initializes the tests package
│   ├── test_conflict_detector.py # Unit tests for ConflictDetector
│   ├── test_translation_checker.py # Unit tests for TranslationChecker
│   └── test_openai_client.py   # Unit tests for OpenAIClient
├── .env.local                  # Contains OpenAI API key
├── .gitignore                  # Specifies files to ignore in version control
├── requirements.txt            # Lists project dependencies
├── setup.py                    # Setup script for the project
└── README.md                   # Documentation for the project
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd translation-manager
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables by creating a `.env.local` file with your OpenAI API key:
   ```
   OPENAI_API_KEY='your_api_key_here'
   ```

## Usage

To run the application, execute the following command:
```
python src/main.py
```

This will initiate the process of detecting merge conflicts and managing translations according to the defined rules.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.