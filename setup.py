"""
Generate real-world insights and business case studies with strategic AI.
"""

from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="thinking-dataset",
    version="0.0.1",
    author="Kara Rawson",
    author_email="rawsonkara@gmail.com",
    maintainer="MultiTonic",
    maintainer_email="info@datatonic.ai",
    description="Real-world business insights and case studies with AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MultiTonic/thinking-dataset",
    project_urls={
        "Homepage": "https://github.com/MultiTonic/thinking-dataset",
        "Documentation":
        "https://github.com/MultiTonic/thinking-dataset/tree/main/docs",
        "Repository": "https://github.com/MultiTonic/thinking-dataset",
        "Issues": "https://github.com/MultiTonic/thinking-dataset/issues",
        "Changelog":
        "https://github.com/MultiTonic/thinking-dataset/blob/main/CHANGELOG.md",  # noqa
        "Discord": "https://discord.gg/RgxcdVFjpz",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Business",
    ],
    packages=find_packages(exclude=["tests*", "docs*"]),
    python_requires=">=3.10",
    install_requires=[
        "huggingface_hub[cli]>=0.19.0",
        "datasets>=2.15.0",
        "PyPDF2>=3.0.0",
        "python-dotenv>=1.0.0",
        "click>=8.1.7",
        "requests>=2.31.0",
        "rich>=13.7.0",
        "sqlite-utils>=3.35.1",
        "pytest>=7.4.3",
        "pytest-html>=4.1.1",
        "pytest-cov>=4.1.0",
        "loguru>=0.7.2",
        "pandas>=2.1.3",
        "numpy<2.0.0",
        "scikit-learn>=1.3.2",
        "sqlalchemy>=2.0.23",
        "tqdm>=4.66.1",
        "pydantic>=2.5.2",
        "python-statemachine>=2.1.2",
        "jsonschema>=4.20.0",
        "ollama>=0.1.4",
        "tenacity>=8.2.3",
        "lorem-text>=2.1.1",
    ],
    extras_require={
        "dev": [
            "black>=23.11.0",
            "isort>=5.12.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
            "pre-commit>=3.5.0",
        ],
        "test": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pytest-html>=4.1.1",
            "pytest-mock>=3.12.0",
            "pytest-asyncio>=0.21.1",
        ],
        "docs": [
            "sphinx>=7.2.6",
            "sphinx-rtd-theme>=1.3.0",
            "sphinx-autodoc-typehints>=1.24.0",
        ],
        "gpu": [
            "torch>=2.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "thinking-dataset=thinking_dataset.main:cli",
        ],
    },
    keywords=[
        "dataset",
        "ai",
        "machine-learning",
        "business",
        "case-studies",
        "strategic-ai",
    ],
    package_data={
        "thinking_dataset": [
            "config/*.yaml",
            "assets/templates/*.md",
            "assets/prompts/*.md",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    license="MIT",
)
