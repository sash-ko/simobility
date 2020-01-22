# simobility

**simobility** - light-weight mobility simulation framework. Best for quick prototyping

**simobility** is a human-friendly Python framework that helps scientists and engineers prototype and compare fleet optimization algorithms (autonomous and human-driven vehicles).

Some example of such algorithms:
* [T-Share: A Large-Scale Dynamic Taxi Ridesharing Service](https://www.microsoft.com/en-us/research/publication/t-share-a-large-scale-dynamic-taxi-ridesharing-service/) - one of the classical ridesharing algorithms 
* [MOVI: A Model-Free Approach to Dynamic Fleet Management](https://arxiv.org/abs/1804.04758) - Deep Q-network that directly learns the optimal vehicle dispatch policy
* [Autonomous Vehicle Fleet Sizes Required to Serve Different Levels of Demand](https://www.research-collection.ethz.ch/handle/20.500.11850/104743) - fleet sizing problem
* [On-demand high-capacity ride-sharing via dynamic trip-vehicle assignment](https://www.pnas.org/content/114/3/462)

## Framework

**simobility** provides a set of building blocks for designing simulations:
- clock
- dispatcher
- demand model
- vehicles
- routers
- ...

## Simulation logs

Simulator logs detailed information about each state change. For example:

```bash
2020-01-22 19:44:48,082;0;vehicle;a2f7647a952e1b8b356f8bd11711eb57;None;offline;idling;{'vehicle_id': 'a2f7647a952e1b8b356f8bd11711eb57', 'position': {'lat': 40.71983, 'lon': -74.00852}}
2020-01-22 19:44:48,897;0;booking;cae48e22e92e198905e27f81f0e520eb;None;created;pending;{'pickup': {'lat': 40.72739, 'lon': -73.98882}, 'dropoff': {'lat': 40.73417, 'lon': -73.98341}, 'position': {'lat': 40.72739, 'lon': -73.98882}}
2020-01-22 19:44:48,905;0;vehicle;601e5b45785116080d650372e90794df;2eefab1a61764d7da438d564285c2630;idling;moving_to;{'vehicle_id': '601e5b45785116080d650372e90794df', 'itinerary_id': '2eefab1a61764d7da438d564285c2630', 'itinerary_created_at': 0, 'eta': 7, 'pickup': 'cae48e22e92e198905e27f81f0e520eb', 'position': {'lat': 40.72439, 'lon': -73.98746}, 'destination': {'lat': 40.72739, 'lon': -73.98882}, 'route_duration': 7, 'route_distance': 0.35272271051930876, 'actual_duration': 0, 'actual_distance': 0.0}
2020-01-22 19:44:48,906;0;booking;cae48e22e92e198905e27f81f0e520eb;2eefab1a61764d7da438d564285c2630;pending;matched;{'vehicle_id': '601e5b45785116080d650372e90794df', 'itinerary_id': '2eefab1a61764d7da438d564285c2630', 'itinerary_created_at': 0, 'position': {'lat': 40.72739, 'lon': -73.98882}}
2020-01-22 19:44:48,907;0;booking;c0d2f3a2f7d558cf865bd310d142c31c;9d3c04896a2940068d37edf44bd00a53;pending;matched;{'vehicle_id': 'd48dd9f354366c219c3ecb54c5cefdd8', 'itinerary_id': '9d3c04896a2940068d37edf44bd00a53', 'itinerary_created_at': 0, 'position': {'lat': 40.75455, 'lon': -73.96867}}
```

As a result, each step of a simulation can be visualized and various metrics can be calculated. For example:

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

<img src="./img/example.png" width="50%">

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

## Read simulation output

```python
data = pd.read_csv('simulation_output.csv', sep=';', header=None, names=['datetime', 'clock_time', 'object_type', 'uuid', 'itinerary_id', 'from_state', 'to_state', 'details'], parse_dates=['datetime'], converters={'details': lambda v: eval(v)})

details = data.details.apply(pd.Series)
# or

from pandas.io.json import json_normalize
details = json_normalize(data.details)
```
