import logging
import os

app_name = "manifest_build"
_log_level = os.getenv("LOG_LEVEL", "INFO")

console_handler = logging.StreamHandler()
console_handler.setLevel(_log_level)
formatter = logging.Formatter(
    "%(levelname)s : %(asctime)s : %(name)s : %(module)s.%(funcName)s: line(%(lineno)s) : %(message)s"
)
console_handler.setFormatter(formatter)
logger_b = logging.getLogger(app_name)
logger_b.setLevel(_log_level)
logger_b.addHandler(console_handler)
logger_b.propagate = False
logger_b.info(f"Logging configured for {app_name} at level {_log_level}")