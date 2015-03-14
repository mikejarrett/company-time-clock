# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name = "TimeClock",
    version = "0.1.0",
    packages = find_packages(),
    scripts = [],

    install_requires = [],

    package_data = {
        '': ['*.txt', '*.rst'],
    },

    author = "Mike Jarrett",
    author_email = "mike.d.jarrett at gmail dot com",
    description = "A simple time keeping application",
    license = "MIT",
    keywords = "time keeping clock",
    url = "https://github.com/mikejarrett/company-time-clock",
)
