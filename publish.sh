python setup.py sdist
twine upload dist/*

rm -rf simobility.egg-info/
rm -rf dist/