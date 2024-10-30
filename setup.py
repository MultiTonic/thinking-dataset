from setuptools import setup, find_packages

setup(
    name='thinking-dataset',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'distillabel',
        'ollama',
        # Add other dependencies here
    ],
    entry_points={
        'console_scripts': [
            'thinking-dataset = thinking_dataset.main:main',
        ],
    },
)
