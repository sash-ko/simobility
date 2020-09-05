.PHONY = test run-example publish

test:
	python -m pytest

run-example:
	python examples/simple_simulation.py

publish:
	python setup.py sdist
	twine upload dist/*
	rm -rf simobility.egg-info/
	rm -rf dist/