"""
Setup script for Digital Communication Simulator
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="digital-comm-simulator",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="End-to-end digital communication system simulator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/digital-comm-simulator",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Communications",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.24.3",
        "scipy>=1.10.1",
        "matplotlib>=3.7.1",
        "streamlit>=1.25.0",
        "tqdm>=4.65.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "jupyter>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "comm-sim=main:main",
        ],
    },
)