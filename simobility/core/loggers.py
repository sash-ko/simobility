import logging


def configure_main_logger(file_name):

    disable_loggers()

    logger = logging.getLogger("state_changes")

    ch = logging.FileHandler(file_name, "w")
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(message)s")
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    logs_schema = 'clock_time;object_type;uuid;itinerary_id;from_state;to_state;lon;lat;details'
    # add header to log file 
    logger.info(logs_schema)

    logging.info(f'Store logs in {file_name}')
    logging.info(f'Logs schema: {logs_schema.split(";")}')


def configure_root_logger(
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


def disable_loggers():

    log = logging.getLogger("urllib3.connectionpool")
    log.setLevel(logging.CRITICAL)

    log = logging.getLogger("transitions.core")
    log.setLevel(logging.CRITICAL)
