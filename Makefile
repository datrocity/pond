# python virtualenv
PYTHON_CMD?=python3
VENV_NAME?=.venv
VENV_ACTIVATE=$(VENV_NAME)/bin/activate
VENV_PYTHON=$(VENV_NAME)/bin/python

# paths
SRC_PATH=pond
TESTS_PATH=tests

.PHONY: help
help: ## this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

$(VENV_ACTIVATE): setup.py setup.cfg requirements.txt requirements-*.txt
	@test -d $(VENV_NAME) || $(PYTHON_CMD) -m venv $(VENV_NAME) && \
	$(VENV_PYTHON) -m pip install --upgrade pip && \
	$(VENV_PYTHON) -m pip install -r requirements-dev.txt && \
	touch $(VENV_ACTIVATE)

.PHONY: setup
setup: $(VENV_ACTIVATE) ## setup the virtual environment

.PHONY: clean
clean: ## delete the virtual environment
	@rm -rf $(VENV_NAME)

.PHONY: lint
lint: setup ## run the static type checker and the linter
	@. $(VENV_ACTIVATE) && \
	flake8 $(SRC_PATH) && \
	mypy $(SRC_PATH) --strict

.PHONY: test
test: ONLY?=*
test: setup ## run the unit tests
	@. $(VENV_ACTIVATE) && \
	pytest $(TESTS_PATH)/test_*$(ONLY)*.py

.PHONY: watch
watch: ONLY?=*
watch: setup ## watch source files and re-run unit tests on every change
	@. $(VENV_ACTIVATE) && \
	ptw --clear -- $(TESTS_PATH)/test_*$(ONLY)*.py
