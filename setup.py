from setuptools import setup, find_packages

setup(
    name='thinking-dataset',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'huggingface_hub[cli]', 'datasets', 'PyPDF2', 'python-dotenv', 'click',
        'requests', 'rich', 'sqlite-utils', 'pytest', 'pytest-html',
        'pytest-cov', 'loguru', 'pandas', 'numpy', 'scikit-learn',
        'sqlalchemy', 'tqdm', 'pydantic', 'python-statemachine', 'jsonschema',
        'ollama'
    ],
    entry_points={
        'console_scripts': [
            'thinking-dataset = thinking_dataset.main:cli',
        ],
    },
)
