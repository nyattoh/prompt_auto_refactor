from setuptools import setup, find_packages

setup(
    name="prompt-auto-refactor",
    version="1.0.0",
    description="A tool for automatic code refactoring based on natural language prompts",
    author="Claude Code Assistant",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.0",
        "pytest>=7.4.0",
        "pytest-cov>=4.1.0",
    ],
    entry_points={
        'console_scripts': [
            'refactor=src.main:cli',
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)