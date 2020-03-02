# simobility

**simobility** is a light-weight mobility simulation framework. Best for quick prototyping

**simobility** is a human-friendly Python framework that helps scientists and engineers to prototype and compare fleet optimization algorithms (autonomous and human-driven vehicles). It provides a set of building blocks that can be used to design different simulation scenarious, run simulations and calculate metrics. It is easy to plug in custom demand models, customer behavior models, fleet types, spatio-temporal models (for example, use [OSRM](http://project-osrm.org/) for routing vehicles and machine learning models trained on historical data to predict [ETA](https://en.wikipedia.org/wiki/Estimated_time_of_arrival)).

### Motivation

Create an environment for experiments with machine learning algorithms for decision-making problems in mobility services and compare them to classical solutions.

<img src="./examples/moving_vehicles.gif" width="35%" align="right">

Some examples:
* [Deep Reinforcement Learning with Applications in Transportation](https://outreach.didichuxing.com/tutorial/AAAI2019/)

* [T. Oda and C. Joe-Wong, "Movi: A model-free approach to dynamic fleet management". 2018](https://arxiv.org/pdf/1804.04758.pdf)

* [A. Alabbasi, A. Ghosh, and V. Aggarwal, "DeepPool: Distributed model-free algorithm for ride-sharing using deep reinforcement learning", IEEETrans. Intelligent Transportation Systems (to appear). 2019](https://arxiv.org/pdf/1903.03882)

* [C Wang,Y Hou, M Barth, "Data-Driven Multi-step Demand Prediction for Ride-hailing Services Using Convolutional Neural Network". 2019](https://arxiv.org/pdf/1911.03441.pdf)

* [J. Ke, F. Xiao, H. Yang, and J. Ye. Optimizing online matching for ride-sourcing services with multi-agent deep reinforcement learning. 2019](https://arxiv.org/abs/1902.06228)

### Installation

`pip install simobility`

### Contributions and thanks

Thanks to all who contributed to the concept/code:

* [Steffen Häußler](https://www.linkedin.com/in/steffenhaeussler/)
* [Stephen Privitera](https://www.linkedin.com/in/stephen-privitera/)
* [Sultan Imanhodjaev](https://www.linkedin.com/in/imanhodjaev/)
* [Yábir Benchakhtir](https://www.linkedin.com/in/yabirgb/)

### Examples

[Simple simulation example](./examples/simple_simulation.py)

[Taxi service example](./examples/taxi_service.py)

[Log example](./examples/simulation_output_example.csv)


### Benchmarks

Benchmark simulations with `LinearRouter` and `GreedyMatcher`. Simulations will run slower with `OSRMRouter` because `OSRM` cannot process requests as fast as the linear router.

_Processor: 2,3 GHz Dual-Core Intel Core i5; Memory: 8 GB 2133 MHz LPDDR3_

Simulated time | Simulation step | Vehicles | Bookings per hour | Execution time | Generated events | Pickup rate
--- | --- | --- | --- | --- | --- | ---
|1 hour | 10 sec | 50 | 100 | 4 sec | 1082 | 96.97%
|24 hours | 1 min | 50 | 100 | 12 sec | 23745 | 88.37%
|24 hours | 10 sec | 50 | 100 | 20 sec | 23880 | 88.84%
|12 hours | 10 sec | 200 | 100 | 18 sec | 13337 | 99.89%
|12 hours | 10 sec | 50 | 500 | 31 sec | 40954 | 53.92%
|12 hours | 10 sec | 200 | 500 | 46 sec | 65444 | 99.3%
|12 hours | 10 sec | 1000 | 500 | 1 min 48 sec | 66605 | 99.98%
|1 hour | 1 min | 1000 | 1000 | 14 sec | 11486 |
|1 hour | 10 sec | 1000 | 1000 | 18 sec | 11631 |
|24 hours | 1 min | 1000 | 1000 | 5 min 1 sec | 262384 |
|24 hours | 10 sec | 1000 | 1000 | 6 min 20 sec | 262524 |

A heuristic that allows estimating a maximum number of booking a fleet of N vehicles can handle: assume that an avarage trip duration is 15 minute, than 1 vehicle can not more then handle 4 booking per hour and the upper limit for 1000 vehicles is 4000 bookings per hour.

### Metrics example

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

### Simulation logs

The are multiple ways to collect simulation log - use CSV or InMemory log handler or implement your own handler: [loggers](https://github.com/sash-ko/simobility/blob/master/simobility/core/loggers.py)


Read CSV logs with pandas:

```python
import pandas as pd

data = pd.read_csv(
    "simulation_output.csv",
    sep=";",
    converters={"details": lambda v: eval(v)},
)

details = data.details.apply(pd.Series)
```

### Run OSRM

```bash
wget http://download.geofabrik.de/north-america/us/new-york-latest.osm.pbf
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/new-york-latest.osm.pbf
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-partition /data/new-york-latest.osrm
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-customize /data/new-york-latest.osrm
docker run -d -t -i -p 5010:5000 -v "${PWD}:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/new-york-latest.osrm
```
