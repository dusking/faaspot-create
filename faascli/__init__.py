import logging

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

# Set default logging handler to avoid "No handler found" warnings.
logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())
