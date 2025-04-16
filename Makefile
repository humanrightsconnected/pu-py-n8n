.PHONY: setup install dev test lint format clean plan deploy destroy preview venv docs help

# Default Python command
PYTHON = python3
# Virtual environment directory
VENV_DIR = .venv
# UV command
UV = uv
# Pulumi commands
PULUMI = pulumi
PULUMI_STACK = dev

help:
	@echo "pu-py-n8n Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make setup       Create Python virtual environment and install dependencies"
	@echo "  make install     Install dependencies in existing virtual environment"
	@echo "  make dev         Install development dependencies"
	@echo "  make test        Run tests"
	@echo "  make lint        Run linting tools"
	@echo "  make format      Format code with Black and isort"
	@echo "  make clean       Remove build artifacts and virtual environment"
	@echo "  make plan        Preview Pulumi deployment (pulumi preview)"
	@echo "  make deploy      Deploy to Azure (pulumi up)"
	@echo "  make destroy     Destroy Azure resources (pulumi destroy)"
	@echo "  make preview     Preview all resources that would be created/updated/deleted"
	@echo "  make venv        Create a Python virtual environment only"
	@echo "  make docs        Generate documentation"
	@echo "  make help        Show this help message"

# Setup the development environment
setup: venv install dev

# Create a virtual environment
venv:
	$(UV) venv

# Install dependencies
install:
	$(UV) sync

# Install development dependencies
dev:
	$(UV) add --dev pytest pytest-mock black isort flake8 pylint pytest-cov

# Run tests
test:
	$(UV) run pytest

# Run lint checks
lint:
	$(UV) run flake8 src tests
	$(UV) run pylint src tests
	$(UV) run isort --check src tests
	$(UV) run black --check src tests

# Format code
format:
	$(UV) run isort src tests
	$(UV) run black src tests

# Clean up build artifacts and virtual environment
clean:
	rm -rf $(VENV_DIR)
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Preview Pulumi deployment
plan:
	$(PULUMI) preview --stack $(PULUMI_STACK)

# Deploy to Azure
deploy:
	$(PULUMI) up --stack $(PULUMI_STACK)

# Destroy Azure resources
destroy:
	$(PULUMI) destroy --stack $(PULUMI_STACK)

# Show more detailed preview
preview:
	$(PULUMI) preview --stack $(PULUMI_STACK) --diff

# Generate documentation
docs:
	mkdir -p docs
	$(UV) run pdoc --html --output-dir docs src/pu_py_n8n