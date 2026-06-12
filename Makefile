# Makefile for local development of the Datavoid blog

.PHONY: dev venv install run

dev: venv install run

# Create a Python virtual environment in the project root
venv:
	python3 -m venv .venv

# Install all Python dependencies into the venv
install:
	. .venv/bin/activate && pip install -r requirements.txt

# Run a single iteration of the pipeline (draft → critic → publish)
run:
	. .venv/bin/activate && python -m pipeline.schedule --once
