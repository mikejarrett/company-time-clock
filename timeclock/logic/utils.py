# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import OrderedDict
from functools import wraps
from passlib.hash import pbkdf2_sha256
import inspect
import itertools
import logging
import sys
import threading

logger = logging.getLogger(__name__)


class Logged(object):

    def __call__(self, f):
        log = getattr(
            sys.modules[f.__module__], 'log', logging.getLogger(f.__module__)
        )

        def wrapped_f(*args, **kwargs):
            args_name = list(
                OrderedDict.fromkeys(inspect.getargspec(f)[0] + kwargs.keys())
            )
            args_dict = OrderedDict(
                list(itertools.izip(args_name, args)) +
                list(kwargs.iteritems())
            )

            # We don't care about `self` or `cls`
            args_dict.pop('self', None)
            args_dict.pop('cls', None)

            # Build a log_message with argument name and value
            log_message = ', '.join(
                '{}: %r'.format(arg_name.encode('utf-8'))
                for arg_name in args_dict.keys()
            )

            if log_message:
                log_message = '{} -- {}'.format(f.func_name, log_message)
            else:
                log_message = '{} -- No arguments'.format(f.func_name)
            log.debug(log_message, *args_dict.values())

            return f(*args, **kwargs)

        return wrapped_f


def hash_password(password):
    return pbkdf2_sha256.encrypt(password, rounds=200000, salt_size=16)


@Logged()
def validate_password(password, hashed):
    return pbkdf2_sha256.verify(password, hashed)


@Logged()
def seconds_to_hours(seconds):
    return float((seconds / 60.0) / 60.0)


@Logged()
def time_difference_in_hours(start_time, end_time):
    if start_time and end_time:
        return seconds_to_hours((end_time - start_time).total_seconds())
    else:
        return float(0)
