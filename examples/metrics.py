import logging
import json
import pandas as pd
from pprint import pprint
from simobility.core.metrics import calculate_metrics


def print_metrics(file_name, clock):
    logging.info(f'Reading file {file_name}...')

    data = pd.read_csv(
        file_name,
        sep=";",
        converters={"details": lambda v: eval(v)},
    )

    metrics = calculate_metrics(data, clock)

    logging.info('Metrics:')

    metrics = json.loads(
        json.dumps(metrics, sort_keys=False), parse_float=lambda v: round(float(v), 2)
    )

    pprint(metrics, indent=2)
