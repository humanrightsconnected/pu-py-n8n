# PowerShell script to create the directory structure for pu-py-n8n
# Assumes script is run in the pu-py-n8n directory with venv already created

# Script header and info
Write-Host "Creating directory structure for pu-py-n8n project..." -ForegroundColor Green
Write-Host "Assuming script is running in the pu-py-n8n root directory" -ForegroundColor Yellow

# Create src directory and package subdirectory
New-Item -Path "src" -ItemType Directory -Force | Out-Null
New-Item -Path "src\pu_py_n8n" -ItemType Directory -Force | Out-Null

# Create tests directory
New-Item -Path "tests" -ItemType Directory -Force | Out-Null

# Create Python files in src directory
$initContent = @"
"""
pu-py-n8n: A Pulumi Python project for deploying n8n to Azure Kubernetes Service.
"""

__version__ = "0.1.0"
"@
Set-Content -Path "src\pu_py_n8n\__init__.py" -Value $initContent

# Create main module files
$mainFiles = @(
    "main.py",
    "config.py",
    "aks_cluster.py",
    "n8n_deployment.py"
)

foreach ($file in $mainFiles) {
    $content = @"
"""
$(if ($file -eq "main.py") {"Main Pulumi program for deploying n8n to Azure Kubernetes Service."} 
elseif ($file -eq "config.py") {"Configuration management for n8n Azure deployment."} 
elseif ($file -eq "aks_cluster.py") {"Module for creating and configuring an Azure Kubernetes Service (AKS) cluster."} 
else {"Module for deploying n8n to an AKS cluster with PostgreSQL."})
"""

# TODO: Implement module
"@
    Set-Content -Path "src\pu_py_n8n\$file" -Value $content
}

# Create test files
$testInitContent = @"
"""
Test suite for the pu-py-n8n package.
"""
"@
Set-Content -Path "tests\__init__.py" -Value $testInitContent

$testFiles = @(
    "conftest.py",
    "test_aks_cluster.py",
    "test_n8n_deployment.py"
)

foreach ($file in $testFiles) {
    $content = @"
"""
$(if ($file -eq "conftest.py") {"Pytest configuration and fixtures for testing n8n Azure deployment."} 
elseif ($file -eq "test_aks_cluster.py") {"Tests for the AKS cluster module."} 
else {"Tests for the n8n deployment module."})
"""

# TODO: Implement tests
"@
    Set-Content -Path "tests\$file" -Value $content
}

# Create other essential files
$pythonVersionContent = "3.9.16"
Set-Content -Path ".python-version" -Value $pythonVersionContent

# Create empty .gitignore
if (-not (Test-Path ".gitignore")) {
    New-Item -Path ".gitignore" -ItemType File -Force | Out-Null
}

# Create a basic README.md if it doesn't exist
if (-not (Test-Path "README.md")) {
    $readmeContent = @"
# pu-py-n8n

A Pulumi Python project for deploying n8n to Azure Kubernetes Service (AKS).

## Overview

This project provides infrastructure as code for deploying n8n to Azure Kubernetes Service using Pulumi and Python.

## Getting Started

See the documentation for setup and usage instructions.
"@
    Set-Content -Path "README.md" -Value $readmeContent
}

# Create initial pyproject.toml if it doesn't exist
if (-not (Test-Path "pyproject.toml")) {
    $pyprojectContent = @"
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "pu-py-n8n"
version = "0.1.0"
description = "Pulumi deployment of n8n to Azure Kubernetes Service"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
dependencies = [
    "pulumi>=3.0.0,<4.0.0",
    "pulumi-azure-native>=2.0.0",
    "pulumi-kubernetes>=4.0.0",
    "pyyaml>=6.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-mock>=3.10.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "flake8>=6.0.0",
]

[tool.setuptools]
package-dir = {"" = "src"}

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "--import-mode=importlib"

[tool.black]
line-length = 88
target-version = ["py39"]
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 88
"@
    Set-Content -Path "pyproject.toml" -Value $pyprojectContent
}

# Summary message
Write-Host "Directory structure created successfully!" -ForegroundColor Green
Write-Host @"

Project structure:
pu-py-n8n/
├── .gitignore
├── .python-version
├── .venv/ (already exists)
├── pyproject.toml
├── README.md
├── src/
│   └── pu_py_n8n/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── aks_cluster.py
│       └── n8n_deployment.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_aks_cluster.py
    └── test_n8n_deployment.py

Next steps:
1. Install dependencies: uv sync
2. Add development dependencies: uv add --dev pytest pytest-mock black isort flake8
3. Implement the modules and tests
4. Run tests: uv run pytest
"@