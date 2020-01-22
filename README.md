# simobility

**simobility** - light-weight mobility simulation framework. Best for quick prototyping

**simobility** is a human-friendly Python framework that helps scientists and engineers prototype and compare fleet optimization algorithms (autonomous and human-driven vehicles).

Some example of such algorithms:
* [T-Share: A Large-Scale Dynamic Taxi Ridesharing Service](https://www.microsoft.com/en-us/research/publication/t-share-a-large-scale-dynamic-taxi-ridesharing-service/) - one of the classical ridesharing algorithms 
* [MOVI: A Model-Free Approach to Dynamic Fleet Management](https://arxiv.org/abs/1804.04758) - Deep Q-network that directly learns the optimal vehicle dispatch policy
* [Autonomous Vehicle Fleet Sizes Required to Serve Different Levels of Demand](https://www.research-collection.ethz.ch/handle/20.500.11850/104743) - fleet sizing problem
* [On-demand high-capacity ride-sharing via dynamic trip-vehicle assignment](https://www.pnas.org/content/114/3/462)

Ride sharing pseudocode:

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
