from setuptools import setup, find_packages

setup(
    name='translation-manager',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A tool for managing translations and detecting merge conflicts in codebases.',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'openai',
        'difflib',
        'pytest'
    ],
    entry_points={
        'console_scripts': [
            'translation-manager=main:main',
        ],
    },
)