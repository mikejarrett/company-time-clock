# -*- coding: utf-8 -*-
from datetime import datetime

from logic.utils import hash_password

WTF_CSRF_ENABLED = True
SECRET_KEY = hash_password(datetime.now().isoformat())
