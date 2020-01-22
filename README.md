# simobility

simobility - light-weight mobility simulation framework. Best for quick prototyping

Provides simple interface for matching/dispatching/rebalancing.

Ride sharing example:

```python
dispatcher = Dispatcher()
fleet = Fleet()

taxi_1 = Vehicle()
taxi_2 = Vehicle()
fleet.infleet([taxi_1, taxi_2])

customer_1 = Booking(pickup1, dropoff1)
customer_2 = Booking(pickup2, dropoff2)

router = Router()
distance_matrix = router.calculate_distance_marix(
    [customer_1, customer_2],
    [taxi_1, taxi_2]
)

# ... Find best match between customers and taxies ...

# Create ride sharing itinerary (2 customers in one taxi)
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
```

## 

## Read simulation output

```python
data = pd.read_csv('simulation_output.csv', sep=';', header=None, names=['datetime', 'clock_time', 'object_type', 'uuid', 'itinerary_id', 'from_state', 'to_state', 'details'], parse_dates=['datetime'], converters={'details': lambda v: eval(v)})

details = data.details.apply(pd.Series)
# or

from pandas.io.json import json_normalize
details = json_normalize(data.details)
```
