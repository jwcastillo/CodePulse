#!/usr/bin/env python3
"""
Setup script for CodePulse.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

setup(
    name="codepulse",
    version="2.0.0",
    description="Advanced Code Quality Analysis Tool for Java, JavaScript, and TypeScript",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="CodePulse Team",
    author_email="team@codepulse.dev",
    url="https://github.com/yourusername/codepulse",
    packages=find_packages(where="src"),
    py_modules=["cli"],  # the console script imports the top-level module src/cli.py
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies - uses only Python stdlib
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "codepulse=cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="code-analysis static-analysis java javascript typescript nextjs nodejs quality",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/codepulse/issues",
        "Source": "https://github.com/yourusername/codepulse",
        "Documentation": "https://codepulse.dev/docs",
    },
)
