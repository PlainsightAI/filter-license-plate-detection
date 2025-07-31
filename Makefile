# ---------------------------------
# Repo-specific variables
# ---------------------------------

VERSION ?= $(shell cat VERSION)

# Define these variables for consistency in the repo
REPO_NAME ?= filter-license-plate-detection
REPO_NAME_SNAKECASE ?= filter_license_plate_detection
REPO_NAME_PASCALCASE ?= FilterLicensePlateDetection

export VERSION

# Unique pipeline configuration for this repo
# TODO: Add GAR source support via dlCache
PIPELINE := \
	- VideoIn \
		--sources 'file://example_video.mp4!loop' \
	- $(REPO_NAME_SNAKECASE).filter.$(REPO_NAME_PASCALCASE) \
		--mq_log pretty \
	- Webvis
# ---------------------------------
# Repo-specific targets
# ---------------------------------

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: download-model
download-model:
	@if [ ! -f model.pth ]; then \
		echo "model not found, downloading model archive..."; \
		curl -L -o model.zip https://models.openfilter.io/license_plate_detection_model/v0.1.0.zip; \
		echo "Unzipping model archive to current directory..."; \
		unzip -o model.zip; \
		echo "Removing model.zip..."; \
		rm model.zip; \
	else \
		echo "model already exists, skipping download."; \
	fi

.PHONY: install
install: download-model
	pip install -e .[dev] \
		--extra-index-url https://python.openfilter.io/simple

.PHONY: run
run:  ## Run locally with supporting Filters in other processes
	openfilter run ${PIPELINE}

.PHONY: test
test:  ## Run unit tests
	pytest -vv -s tests/ --junitxml=results/pytest-results.xml

.PHONY: test-coverage
test-coverage:  ## Run unit tests and generate coverage report
	@mkdir -p Reports
	@pytest -vv --cov=tests --junitxml=Reports/coverage.xml --cov-report=json:Reports/coverage.json -s tests/
	@jq -r '["File Name", "Statements", "Missing", "Coverage%"], (.files | to_entries[] | [.key, .value.summary.num_statements, .value.summary.missing_lines, .value.summary.percent_covered_display]) | @csv'  Reports/coverage.json >  Reports/coverage_report.csv
	@jq -r '["TOTAL", (.totals.num_statements // 0), (.totals.missing_lines // 0), (.totals.percent_covered_display // "0")] | @csv'  Reports/coverage.json >>  Reports/coverage_report.csv

.PHONY: build-wheel
build-wheel:  ## Build python wheel
	python -m pip install setuptools build wheel twine setuptools-scm --index-url https://pypi.org/simple
	python -m build --wheel

.PHONY: clean
clean:  ## Delete all generated files and directories
	sudo rm -rf build/ cache/ dist/ $(REPO_NAME_SNAKECASE).egg-info/ telemetry/
	find . -name __pycache__ -type d -exec rm -rf {} +