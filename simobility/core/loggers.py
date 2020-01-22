import logging


_log = logging.getLogger("transitions.core")
_log.setLevel(logging.CRITICAL)

_log = logging.getLogger("urllib3.connectionpool")
_log.setLevel(logging.CRITICAL)


def config_state_changes(file_name):

    logger = logging.getLogger("state_changes")

    ch = logging.FileHandler(file_name, "w")
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s;%(message)s")
    ch.setFormatter(formatter)

    logger.addHandler(ch)


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
