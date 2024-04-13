import logging

LOG_FORMAT = "[%(asctime)s] [%(process)s] [%(levelname)s] [%(name)s]: %(message)s"


def get_logger(name: str, log_level: int = logging.INFO) -> logging.Logger:
    """Returns a logger with a local console and file handler

    Args:
        name (str): Name of logger
        log_level (int, optional): Log level. Defaults to logging.INFO.

    Returns:
        logging.Logger: Logger
    """
    log = logging.getLogger(name)
    fmt = logging.Formatter(LOG_FORMAT)
    log.setLevel(log_level)

    if log.hasHandlers():
        log.handlers.clear()

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    log.addHandler(ch)
    return log
