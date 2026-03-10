import logging
import sys


def setup_logging():
    root = logging.getLogger()

    if root.handlers:
        return

    root.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | file: %(name)s | func: %(funcName)s | %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)

    root.addHandler(stream_handler)


def get_logger(name: str):
    setup_logging()
    return logging.getLogger(name)