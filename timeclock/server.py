#!/usr/bin/env python
# -*- coding: utf-8 -*-

from settings import DEBUG
from webapp import app


if __name__ == '__main__':
    app.run(debug=DEBUG)
