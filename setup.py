"""
Alert Noise Analyzer - Setup Configuration
A production-tested framework for analyzing and reducing alert fatigue in monitoring systems.
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="alert-noise-analyzer",
    version="1.0.0",
    author="Sneha",
    author_email="sneha.17.r@gmail.com",
    description="Production-tested framework for analyzing and reducing alert fatigue in monitoring systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/snehar-dev/alert-noise-framework",
    
    py_modules=[
        'alert_analyzer',
        'generate_report',
        'cli',
        'generator',
    ],
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    
    python_requires=">=3.8",
    
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
    ],
    
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=3.0.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
        ],
    },
    
    entry_points={
        'console_scripts': [
            'analyze-alerts=cli:main',
            'generate-alerts=generator:main',
        ],
    },
    
    include_package_data=True,
    zip_safe=False,
)
