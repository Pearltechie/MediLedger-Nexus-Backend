#!/usr/bin/env python3
"""
Setup script for MediLedger Nexus Backend
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="mediledger-nexus",
    version="0.1.0",
    author="MediLedger Nexus Team",
    author_email="team@mediledgernexus.com",
    description="Decentralized Health Data Ecosystem on Hedera",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mediledgernexus/backend",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "python-multipart>=0.0.6",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-dotenv>=1.0.0",
        "cryptography>=41.0.0",
        "aiofiles>=23.2.1",
        "httpx>=0.25.0",
        "sqlalchemy>=2.0.0",
        "alembic>=1.12.0",
        "psycopg2-binary>=2.9.0",
        "redis>=5.0.0",
        "celery>=5.3.0",
        "ipfshttpclient>=0.8.0a2",
        "web3>=6.11.0",
        "py-solc-x>=2.0.0",
        "torch>=2.1.0",
        "numpy>=1.24.0",
        "pandas>=2.1.0",
        "scikit-learn>=1.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.6.0",
            "pre-commit>=3.5.0",
        ],
        "test": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "httpx>=0.25.0",
            "pytest-mock>=3.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mediledger-nexus=mediledger_nexus.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
