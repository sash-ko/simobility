from pandas.io.json import json_normalize


def calculate_metrics(data, clock):
    details = json_normalize(data.details)

    idx = ~details.stop.isna()
    total_distance = details[idx].trip_distance.sum()
    empty_distance = details[idx & (~details.pickup.isna())].trip_distance.sum()

    booking_idx = data.object_type == "booking"
    vehicle_idx = data.object_type == "vehicle"

    waiting_times = data[booking_idx].groupby("uuid").apply(_calc_waiting_time)
    avg_waiting_time = waiting_times[~waiting_times.isna()].mean()
    avg_waiting_time = clock.clock_time_to_seconds(avg_waiting_time)

    trip_times = data[booking_idx].groupby("uuid").apply(_calc_trip_time)
    avg_trip_time = trip_times[~trip_times.isna()].mean()
    avg_trip_time = clock.clock_time_to_seconds(avg_trip_time)

    created = data[booking_idx & (data.to_state == "pending")].shape[0]
    pickups = data[booking_idx & (data.to_state == "pickup")].shape[0]
    dropoffs = data[booking_idx & (data.to_state == "dropoff")].shape[0]
    expired = data[booking_idx & (data.to_state == "expired")].shape[0]
    pickup_rate = pickups / created * 100

    num_steps = clock.clock_time
    num_vehicles = data[vehicle_idx].uuid.unique().shape[0]

    idx = vehicle_idx & (~details.stop.isna())

    total_duration = details[idx].groupby(data[idx].uuid)["trip_duration"].sum()
    avg_utilization = (total_duration / num_steps * 100).mean()
    fleet_utilization = total_duration.sum() / (num_steps * num_vehicles) * 100

    idx = idx & (~details.dropoff.isna())
    total_duration = details[idx].groupby(data[idx].uuid)["trip_duration"].sum()
    paid_utilization = (total_duration / num_steps * 100).mean()
    paid_fleet_utilization = total_duration.sum() / (num_steps * num_vehicles) * 100

    return {
        "num_vehicles": num_vehicles,
        "created": created,
        "expired": expired,
        "pickups": pickups,
        "dropoffs": dropoffs,
        "pickup_rate": pickup_rate,
        # time in seconds
        "avg_waiting_time": avg_waiting_time,
        "avg_trip_time": avg_trip_time,
        "avg_utilization": avg_utilization,
        "fleet_utilization": fleet_utilization,
        "avg_paid_utilization": paid_utilization,
        "fleet_paid_utilization": paid_fleet_utilization,
        "total_distance": total_distance,
        "empty_distance": empty_distance,
        "empty_distance_pcnt": empty_distance / total_distance * 100,
    }


def _calc_waiting_time(item):
    vals = dict(item[["to_state", "clock_time"]].values)
    if "pickup" not in vals:
        return None
    return vals["pickup"] - vals["pending"]


def _calc_trip_time(item):
    vals = dict(item[["to_state", "clock_time"]].values)
    if "dropoff" not in vals:
        return None
    return vals["dropoff"] - vals["pickup"]
