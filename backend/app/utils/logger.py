import logging

try:
    from pythonjsonlogger.json import JsonFormatter
except ImportError:
    from pythonjsonlogger.jsonlogger import JsonFormatter

logger = logging.getLogger("pitwall")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()

formatter = JsonFormatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s"
)

handler.setFormatter(formatter)

logger.addHandler(handler)