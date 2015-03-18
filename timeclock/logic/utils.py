# -*- coding: utf-8 -*-

from passlib.hash import pbkdf2_sha256


def hash_password(password):
    return pbkdf2_sha256.encrypt(password, rounds=200000, salt_size=16)


def validate_password(password, hashed):
    return pbkdf2_sha256.verify(password, hashed)


def seconds_to_hours(seconds):
    return float((seconds / 60.0) / 60.0)


def time_difference_in_hours(start_time, end_time):
    if start_time and end_time:
        return seconds_to_hours((end_time - start_time).total_seconds())
    else:
        return float(0)
