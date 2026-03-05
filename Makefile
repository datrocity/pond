# paths
SRC_PATH=pond
TESTS_PATH=tests

.PHONY: help
help: ## this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: setup
setup: ## install dependencies
	@uv sync --extra dev

.PHONY: clean
clean: ## delete the virtual environment
	@rm -rf .venv

.PHONY: lint
lint: ## run the static type checker and the linter
	@uv run flake8 $(SRC_PATH) && \
	uv run mypy $(SRC_PATH) --strict

.PHONY: test
test: ## run the unit tests
	@uv run pytest $(TESTS_PATH) -v

.PHONY: watch
watch: ONLY?=*
watch: ## watch source files and re-run unit tests on every change
	@uv run ptw --clear -- $(TESTS_PATH)/test_*$(ONLY)*.py
