OSRMFILE := new-york-latest
DOWNLOADURL := http://download.geofabrik.de/north-america/us

.PHONY: test
test:
	python -m pytest

.PHONY: run-example
run-example:
	python examples/simple_simulation.py

.PHONY: publish
publish:
	python setup.py sdist
	twine upload dist/*
	rm -rf simobility.egg-info/
	rm -rf dist/

$(OSRMFILE).osm.pbf:
	wget -N $(DOWNLOADURL)/$@

.PHONY: osrm-graph
osrm-graph:
	docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/$(OSRMFILE).osm.pbf
	docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-partition /data/$(OSRMFILE).osrm
	docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-customize /data/$(OSRMFILE).osrm

.PHONY: run-osrm
run-osrm: $(OSRMFILE).osm.pbf osrm-graph
	docker run -d -t -i -p 5010:5000 -v "${PWD}:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/$(OSRMFILE).osrm

.PHONY: stop-osrm
stop-osrm:
	docker stop $$(docker ps -a -q -f ancestor=osrm/osrm-backend)