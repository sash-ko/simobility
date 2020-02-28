import yaml
import argparse
import logging

import simobility.routers as routers
from simobility.simulator.simulator import Simulator
from simobility.core.loggers import configure_root_logger, configure_main_logger
from metrics import print_metrics
from scenario import create_scenario
from greedy_matcher import GreedyMatcher

"""
Example of a simulation that uses scenario defined in scenario.py and
GreedyMatcher
"""


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Simulation parameters")
    parser.add_argument("--config", help="YAML config")
    args = parser.parse_args()

    with open(args.config) as cfg:
        config = yaml.load(cfg, Loader=yaml.FullLoader)

    configure_root_logger(level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")
    configure_main_logger(config["simulation"]["output"])

    context, demand = create_scenario(config)

    if config["solvers"]["greedy_matcher"]["router"] == "linear":
        router = routers.LinearRouter(
            context.clock, config["routers"]["linear"]["speed"]
        )
    elif config["solvers"]["greedy_matcher"]["router"] == "osrm":
        router = routers.OSRMRouter(
            context.clock, server=config["routers"]["osrm"]["server"]
        )
    else:
        raise Exception("Unknown router")

    logging.info(f"Matcher router {router}")

    matcher = GreedyMatcher(context, router, config)

    simulator = Simulator(matcher, context)
    simulator.simulate(demand, config["simulation"]["duration"])

    # print_metrics(config["simulation"]["output"], context.clock)