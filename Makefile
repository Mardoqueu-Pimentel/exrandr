PYTHON_FILES ?= $(shell find src -type f -name "*.py")

AUTOFLAKE_OPTS ?= --ignore-init-module-imports --remove-all-unused-imports --remove-unused-variables
ISORT_OPTS ?= --multi-line 3 --trailing-comma --line-width 100
BLACK_OPTS ?= --line-length 100 --target-version py38
FLAKE8_OPTS ?= --max-line-length 100 --ignore E203,W503
MYPY_OPTS ?= --ignore-missing-imports

.PHONY: init
init:
	@(test -d git-hooks && find $(PWD)/git-hooks -type f -exec ln -s {} .git/hooks \;) || :
	@echo "Generating dotenv..."
	@./scripts/generate-dotenv > .env

.PHONY: autoflake
autoflake:
	@autoflake $(AUTOFLAKE_OPTS) $(PYTHON_FILES)

.PHONY: autoflake-formatter
autoflake-formatter: AUTOFLAKE_OPTS := $(AUTOFLAKE_OPTS) --in-place
autoflake-formatter: autoflake

.PHONY: autoflake-linter
autoflake-linter: AUTOFLAKE_OPTS := $(AUTOFLAKE_OPTS) --check
autoflake-linter: autoflake

.PHONY: isort
isort:
	@isort $(ISORT_OPTS) $(PYTHON_FILES)

.PHONY: black
black:
	@black $(BLACK_OPTS) $(PYTHON_FILES)

.PHONY: black-formatter
black-formatter: black

.PHONY: black-linter
black-linter: BLACK_OPTS := $(BLACK_OPTS) --check
black-linter: black

.PHONY: format
format: autoflake-formatter isort black

.PHONY: mypy
mypy:
	@mypy $(MYPY_OPTS) $(PYTHON_FILES)

.PHONY: flake8
flake8:
	@flake8 $(FLAKE8_OPTS) $(PYTHON_FILES)

.PHONY: lint
lint: ISORT_OPTS := $(ISORT_OPTS) --check-only
lint: autoflake-linter isort black-linter mypy flake8

.PHONY: test
test:
	@pytest --pyargs exrandr_tests --cov=exrandr -vvv -s -x

.PHONY: check
check: lint test

.PHONY: notebook
notebook:
	@cd notebooks && nohup jupyter-lab &
