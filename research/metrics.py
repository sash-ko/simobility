import logging
import json
import pandas as pd
from pprint import pprint
from simobility.core.metrics import calculate_metrics


def print_metrics(file_name, clock):
    logging.info(f'Reading file {file_name}...')

    columns = [
        "datetime",
        "clock_time",
        "object_type",
        "uuid",
        "itinerary_id",
        "from_state",
        "to_state",
        "lon",
        "lat",
        "details",
    ]

    data = pd.read_csv(
        file_name,
        sep=";",
        header=None,
        names=columns,
        parse_dates=["datetime"],
        converters={"details": lambda v: eval(v)},
    )
    print()
    metrics = calculate_metrics(data, clock)

    metrics = json.loads(
        json.dumps(metrics, sort_keys=False), parse_float=lambda v: round(float(v), 2)
    )

    pprint(metrics, indent=2)
