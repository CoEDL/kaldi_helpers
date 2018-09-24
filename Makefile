install:
	python -m venv venv
	source venv/bin/activate
	pip install -r requirements.txt

test:
	export PYTHONPATH=./src/ && pytest
