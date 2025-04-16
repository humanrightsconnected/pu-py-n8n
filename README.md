# pu-py-n8n

A Pulumi Python project for deploying n8n to Azure Kubernetes Service (AKS).

## Overview

This project provides infrastructure as code for deploying [n8n](https://n8n.io/), a workflow automation platform, to Azure Kubernetes Service (AKS) using Pulumi and Python. The deployment includes:

- An AKS cluster
- PostgreSQL database for n8n
- n8n application with persistent storage
- Proper networking and security configuration

## Prerequisites

- Python 3.9 or later
- [Pulumi CLI](https://www.pulumi.com/docs/install/)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [uv](https://github.com/astral-sh/uv) for Python environment and package management

## Project Structure

```
pu-py-n8n/
├── .gitignore
├── .python-version               # Used by uv to specify Python version
├── .venv/                        # Virtual environment created by uv
├── pyproject.toml                # Project configuration and dependencies
├── uv.lock                       # Lock file for dependencies
├── README.md                     # Project documentation
├── src/
│   └── pu_py_n8n/                # Main package
│       ├── __init__.py
│       ├── main.py               # Main Pulumi program
│       ├── config.py             # Configuration helpers
│       ├── aks_cluster.py        # AKS cluster setup
│       └── n8n_deployment.py     # n8n deployment resources
└── tests/
    ├── __init__.py
    ├── conftest.py               # Pytest configuration and fixtures
    ├── test_aks_cluster.py       # Tests for AKS cluster setup
    └── test_n8n_deployment.py    # Tests for n8n deployment
```

## Getting Started

### 1. Setup Environment

Create a Python virtual environment and install dependencies:

```bash
# Create a new virtual environment
uv venv

# Activate the virtual environment
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Install dependencies
uv sync
```

### 2. Login to Azure

```bash
az login
az account set --subscription <your-subscription-id>
```

### 3. Configure Pulumi

```bash
pulumi stack init dev
pulumi config set azure-native:location eastus
```

Optional configuration:

```bash
# Resource group name (default: n8n-resources)
pulumi config set resourceGroupName your-resource-group-name

# Kubernetes version (default: 1.26.10)
pulumi config set kubernetesVersion 1.26.10

# Node count (default: 1)
pulumi config set nodeCount 2

# Node size (default: Standard_D2_v2)
pulumi config set nodeSize Standard_D4_v2

# PostgreSQL password (auto-generated if not set)
pulumi config set --secret postgresPassword your-postgres-password

# n8n encryption key (auto-generated if not set)
pulumi config set --secret n8nEncryptionKey your-encryption-key

# n8n JWT secret (auto-generated if not set)
pulumi config set --secret n8nJwtSecret your-jwt-secret
```

### 4. Deploy

```bash
pulumi up
```

After deployment completes, Pulumi will output:
- Resource group name
- Kubernetes cluster name
- n8n service endpoint URL
- Kubeconfig for connecting to the cluster

### 5. Connect to n8n

Access n8n through the URL provided in the `n8n_service_endpoint` output.

### 6. Cleanup

To clean up all resources:

```bash
pulumi destroy
```

## Testing

This project includes unit tests using pytest. Run tests with:

```bash
uv run pytest
```

## License

MIT License