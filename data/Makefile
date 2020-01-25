TRIP_DATA:=yellow_feb_1w_trips.csv

download-yellow:
	wget https://s3-us-west-2.amazonaws.com/nyctlc/yellow_tripdata_2015-01-06.csv.gz
	gunzip yellow_tripdata_2015-01-06.csv.gz
	mv yellow_tripdata_2015-01-06.csv yellow_tripdata.csv

download-green:
	wget https://data.cityofnewyork.us/api/views/gi8d-wdg5/rows.csv?accessType=DOWNLOAD
	mv rows.csv\?accessType\=DOWNLOAD green_tripdata.csv

filter:
	head -n 1 yellow_tripdata.csv > $(TRIP_DATA)
	# First week of Feb 2015
	grep "^\d,2015-02-0[1-7] " yellow_tripdata.csv >> $(TRIP_DATA)

preprocess:
	python3 preprocess_data.py --data-file=$(TRIP_DATA) --geofence-file=nyc_geofence.geojson --output-file=rides.feather

clean:
	rm yellow_*
	rm *.csv
	rm $(TRIP_DATA)