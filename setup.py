"""
Setup configuration for Arweave Today AI Podcaster.
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "An intelligent, automated podcast generator for Arweave ecosystem news."

# Read requirements
def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return []

setup(
    name="arweave-today-podcaster",
    version="1.0.0",
    author="Arweave Ecosystem",
    author_email="contact@arweave.org",
    description="An intelligent, automated podcast generator for Arweave ecosystem news",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/arweave-today-ai-podcaster",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "isort>=5.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "arweave-podcaster=arweave_podcaster.core.podcast_generator:main",
        ],
    },
    include_package_data=True,
    package_data={
        "arweave_podcaster": ["*.md", "*.txt"],
    },
    zip_safe=False,
)
