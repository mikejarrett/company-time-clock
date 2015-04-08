# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from settings import DB_LOCATION, DEBUG


engine = create_engine(
    'sqlite:///{}'.format(DB_LOCATION), echo=DEBUG, convert_unicode=True
)

Session = sessionmaker(bind=engine)
session = Session()
