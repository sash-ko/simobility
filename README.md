# simobility

**simobility** is a light-weight mobility simulation framework. Best for quick prototyping

**simobility** is a human-friendly Python framework that helps scientists and engineers prototype and compare fleet optimization algorithms (autonomous and human-driven vehicles). It provides a set of building blocks that can be used to design different simulation scenarious, run simulations and calculate metrics. It is easy to plug in custom demand models, customer behavior models, fleet types, spatio-temporal models (for example, use [OSRM](http://project-osrm.org/) for routing vehicles and machine learning models trained on historical data to predict [ETA](https://en.wikipedia.org/wiki/Estimated_time_of_arrival)).

### Motivation

Create an environment for experiments with [AI techniques](https://github.com/sash-ko/ai-transportation) that can be applied to a real-life problem and compare them to *classical* solutions.

<img src="./img/sim.gif" width="35%" align="right">

Some examples:
* [Deep Reinforcement Learning with Applications in Transportation](https://outreach.didichuxing.com/tutorial/AAAI2019/)

* [T. Oda and C. Joe-Wong, "Movi: A model-free approach to dynamic fleet management". 2018](https://arxiv.org/pdf/1804.04758.pdf)

* [A. Alabbasi, A. Ghosh, and V. Aggarwal, "DeepPool: Distributed model-free algorithm for ride-sharing using deep reinforcement learning", IEEETrans. Intelligent Transportation Systems (to appear). 2019](https://arxiv.org/pdf/1903.03882)

* [C Wang,Y Hou, M Barth, "Data-Driven Multi-step Demand Prediction for Ride-hailing Services Using Convolutional Neural Network". 2019](https://arxiv.org/pdf/1911.03441.pdf)

* [J. Ke, F. Xiao, H. Yang, and J. Ye. Optimizing online matching for ride-sourcing services with multi-agent deep reinforcement learning. 2019](https://arxiv.org/abs/1902.06228)

### Installation

`pip install simobility`

### Contributions and Thanks

Thanks to all who contributed to the concept/code:

* [Steffen Häußler](https://www.linkedin.com/in/steffenhaeussler/)
* [Stephen Privitera](https://www.linkedin.com/in/stephen-privitera/)
* [Sultan Imanhodjaev](https://www.linkedin.com/in/imanhodjaev/)
* [Yábir Benchakhtir](https://www.linkedin.com/in/yabirgb/)

## Framework

**simobility** provides a set of building blocks for designing simulations:
- clock
- dispatcher
- demand model
- vehicles
- routers
- ...


## Pseudocode:

```python
dispatcher = Dispatcher()

# Fleet model
fleet = Fleet()
taxi_1 = Vehicle()
taxi_2 = Vehicle()
fleet.infleet([taxi_1, taxi_2])

# Demand model
customer_1 = Booking(pickup1, dropoff1)
customer_2 = Booking(pickup2, dropoff2)

# Spatial model
router = Router()
distance_matrix = router.calculate_distance_marix(
    [customer_1, customer_2],
    [taxi_1, taxi_2]
)

#
# ... Find best match between customers and taxies ...
# Prototype and compare different supply-demand matching algorithms
#

# Create a ride sharing order for taxi_1
itinerary = Itinerary(taxi_1)

# Pickup customer #1
itinerary.move_to(customer_1.pickup)
itinerary.pickup(customer_1)

# Pickup customer #2
itinerary.move_to(customer_2.pickup)
itinerary.pickup(customer_2)

# Dropoff customer #2
itinerary.move_to(customer_2.dropoff)
itinerary.dropoff(customer_2)

# Dropoff customer #1
itinerary.move_to(customer_1.dropoff)
itinerary.dropoff(customer_1)

# Go to parking and wait there
itinerary.move_to(parking)
itinerary.wait(10)

# Dispatch taxies
dispatcher.dispatch(itinerary)

# Analyze logs, calculate metrics/KPIs, create visualizations...
```

## Metrics example

```json
{
    "avg_paid_utilization": 63.98,
    "avg_utilization": 96.87,
    "avg_waiting_time": 292.92,
    "created": 3998,
    "dropoffs": 589,
    "empty_distance": 640.37,
    "empty_distance_pcnt": 33.67,
    "fleet_paid_utilization": 63.98,
    "fleet_utilization": 96.87,
    "num_vehicles": 50,
    "pickup_rate": 15.48,
    "pickups": 619,
    "total_distance": 1902.04,
}
```

## Simulation logs

Simulator outputs information about each state change - [simulation log example](./examples/simulation_log_small.csv)

## Read simulation logs

```python
import pandas as pd
from pandas.io.json import json_normalize

data = pd.read_csv(
    "simulation_output.csv",
    sep=";",
    converters={"details": lambda v: eval(v)},
)

details = data.details.apply(pd.Series)
# same as:
# details = json_normalize(data.details)
```

## Run OSRM

```bash
wget http://download.geofabrik.de/north-america/us/new-york-latest.osm.pbf
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/new-york-latest.osm.pbf
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-partition /data/new-york-latest.osrm
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-customize /data/new-york-latest.osrm
docker run -d -t -i -p 5010:5000 -v "${PWD}:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/new-york-latest.osrm
```
