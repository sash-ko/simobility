import logging
import json
from collections import OrderedDict


class CSVFileHandler(logging.FileHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.columns = [
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

        self.header = ';'.join(self.columns)

    def emit(self, record):
        if not isinstance(record.msg, str):
            record.msg = self.format_message(record.msg)
        super().emit(record)

    def format_message(self, state_info: OrderedDict) -> str:
        strings = []
        for column in self.columns:
            item = state_info.get(column)
            try:
                if item is None:
                    item = ""
                elif isinstance(item, dict):
                    item = json.dumps(item, separators=(",", ":"))
                else:
                    item = str(item)
            # catche error json.encoder.JSONEncoder
            except TypeError:
                item = str(item)

            strings.append(item)

        msg = ";".join(strings)
        return msg


def get_sim_logger():
    return logging.getLogger("state_changes")


def configure_main_logger(file_name):

    disable_loggers()

    logger = logging.getLogger("state_changes")

    ch = CSVFileHandler(file_name, "w")

    ch.setLevel(logging.INFO)

    formatter = logging.Formatter("%(message)s")
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    logger.info(ch.header)


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
