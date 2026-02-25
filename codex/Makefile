.PHONY: test check clean analyze

PY ?= python3

check:
	$(PY) -m py_compile php_analyzer.py
	$(PY) -m unittest -v

test: check

analyze:
	@if [ -z "$(DIR)" ]; then echo "Usage: make analyze DIR=/path/to/php/project" >&2; exit 2; fi
	$(PY) php_analyzer.py "$(DIR)"

clean:
	rm -rf __pycache__ .pytest_cache
	rm -f analysis_report.json

