.PHONY: help
help:
	@echo "make help                      - show commands that can be run"
	@echo "make install                   - install project requirements"
	@echo "make tests                     - run all tests"
	@echo "make coverage                  - run all tests and collect coverage"

.PHONY: install
install:
	@pip install -r requirements.txt

.PHONY: database
database:
	@./manage.py migrate
	@./manage.py loaddata api/fixtures/initial_data_api.json

.PHONY: smtpd
smtpd:
	@python -m smtpd -n -c DebuggingServer localhost:1025

.PHONY: tests
tests:
	@./manage.py test

.PHONY: coverage
coverage:
	@coverage run --source=. ./manage.py test
	@coverage html

ifndef VERBOSE
.SILENT:
endif
