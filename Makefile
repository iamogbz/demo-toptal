.PHONY: help
help:
	@echo "make help                      - show commands that can be run"
	@echo "make install                   - install project requirements"
	@echo "make tests                     - run all tests"
	@echo "make coverage                  - run all tests and collect coverage"

.PHONY: install
install:
	@pip install -r requirements.txt

.PHONY: tests
tests:
	@ ./manage.py test

.PHONY: coverage
coverage:
	@coverage run --source=. ./manage.py test
	@coverage html

ifndef VERBOSE
.SILENT:
endif
