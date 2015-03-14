# -*- coding: utf-8 -*-

from passlib.hash import pbkdf2_sha256


def hash_password(password):
    return pbkdf2_sha256.encrypt(password, rounds=200000, salt_size=16)


def validate_password(password, hashed):
    return pbkdf2_sha256.verify(password, hashed)
