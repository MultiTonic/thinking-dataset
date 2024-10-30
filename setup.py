from setuptools import setup, find_packages

setup(
    name='thinking-dataset',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'distilabel',
        'huggingface_hub',
        'datasets',
        'PyPDF2',
        'pyarrow',
        'openai',
        'ollama',
        'python-dotenv',
        'testcontainers',
        'requests',
        'typing-extensions',
        'torch',
        'psutil'
    ],
    entry_points={
        'console_scripts': [
            'thinking-dataset = thinking_dataset.main:main',
        ],
    },
)
