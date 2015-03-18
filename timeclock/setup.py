#!/usr/bin/env python
# -*- coding: utf-8 -*-

from logic.models import Base, User, engine, session


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    user = session.query(User).filter_by(username='admin').first()
    if user is None:
        user = User(username='admin', fullname='Admin User')
        user.set_password('admin')
