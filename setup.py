#!/usr/bin/env python3
"""
Setup script for GentooUI - A Text User Interface for Gentoo Linux Installation
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="gentooui",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Text User Interface for Gentoo Linux Installation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/gentooui",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "gentooui=gentooui.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "gentooui": ["configs/*.yaml", "templates/*.j2"],
    },
)
