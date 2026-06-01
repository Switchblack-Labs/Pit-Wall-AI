import logging

# pythonjsonlogger moved JsonFormatter to `pythonjsonlogger.json` in newer
# versions; fall back to the legacy module so both work.
try:
    from pythonjsonlogger.json import JsonFormatter
except ImportError:  # pragma: no cover - older pythonjsonlogger
    from pythonjsonlogger.jsonlogger import JsonFormatter

logger = logging.getLogger("pitwall")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()

formatter = JsonFormatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s"
)

handler.setFormatter(formatter)

logger.addHandler(handler)