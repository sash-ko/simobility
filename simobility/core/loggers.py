import logging


_log = logging.getLogger("transitions.core")
_log.setLevel(logging.CRITICAL)

_log = logging.getLogger("urllib3.connectionpool")
_log.setLevel(logging.CRITICAL)


def config_state_changes(file_name):

    logger = logging.getLogger("state_changes")

    ch = logging.FileHandler(file_name, "w")
    ch.setLevel(logging.DEBUG)
    # formatter = logging.Formatter("%(asctime)s;%(message)s", datefmt='%Y-%m-%d %H:%M:%S')
    formatter = logging.Formatter("%(message)s")
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    logs_schema = 'clock_time;object_type;uuid;itinerary_id;from_state;to_state;lon;lat;details'
    logger.info(logs_schema)

    logging.info(f'Logs schema: {logs_schema.split(";")}')


def configure_root(
    level=logging.DEBUG, format="%(name)s %(asctime)s %(levelname)s: %(message)s"
):
    class RootFilter(logging.Filter):
        def filter(self, record):
            return record.name == "root"

    logger = logging.getLogger()
    logger.setLevel(level)
    ch = logging.StreamHandler()

    formatter = logging.Formatter(format)
    ch.setFormatter(formatter)
    ch.addFilter(RootFilter())
    logger.addHandler(ch)
