PYTHON_BINS ?= ./.venv/bin
PYTHON ?= ${PYTHON_BINS}/python
PYTHONPATH ?= ${PWD}/src

.DEFAULT_GOAL := help

help:
# @link https://github.com/marmelab/javascript-boilerplate/blob/master/makefile
	@grep -P '^[a-zA-Z/_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: .venv ## Install the Python dependencies
	${PYTHON_BINS}/poetry install

.PHONY: code-quality/all
code-quality/all: code-quality/black code-quality/isort  ## Run all our code quality tools

.PHONY: code-quality/black
code-quality/black: black_opts ?=
code-quality/black: ## Automated 'a la Prettier' code formatting
# @link https://black.readthedocs.io/en/stable/
	@${PYTHON_BINS}/black ${black_opts} build_readme.py

.PHONY: code-quality/isort
code-quality/isort: isort_opts ?=
code-quality/isort: ## Automated Python imports formatting
	@${PYTHON_BINS}/isort --settings-file=pyproject.toml ${isort_opts} build_readme.py

.venv: ## Initialises the Python virtual environment in a ".venv" folder
	python -m venv .venv
	${PYTHON_BINS}/pip install -U pip poetry
