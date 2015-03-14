# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import DB_LOCATION, DEBUG


engine = create_engine('sqlite:///{}'.format(DB_LOCATION), echo=DEBUG)

Session = sessionmaker(bind=engine)
session = Session()
