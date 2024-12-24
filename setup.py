from setuptools import setup, find_packages

setup(
    name='thinking-dataset',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'huggingface_hub[cli]',
        'datasets',
        'PyPDF2',
        'python-dotenv',
        'requests',
        'rich',
        'sqlite-utils',
        'pytest',
        'loguru',
        'pandas',
        'numpy',
        'scikit-learn',
        'sqlalchemy',
        'tqdm'
    ],
    entry_points={
        'console_scripts': [
            'thinking-dataset = thinking_dataset.main:main',
        ],
    },
)
