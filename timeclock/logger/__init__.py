# -*- coding: utf-8 -*-
# Set default logging handler to avoid "No handler found" warnings.
import logging

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

from logging.config import fileConfig

fileConfig('logger/logging_config.ini', disable_existing_loggers=True)
logging.getLogger(__name__).addHandler(NullHandler())
