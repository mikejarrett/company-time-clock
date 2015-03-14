# -*- coding: utf-8 -*-

from sqlalchemy import (
    Column, DateTime, ForeignKey, Integer, Sequence, String, Table
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

from .db import session, engine
from .utils import hash_password

Base = declarative_base()


class User(Base):

    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    username = Column(String)
    fullname = Column(String)
    password = Column(String)
    punches = relationship('Punch', backref='user')

    def __repr__(self):
        return "<User(usename='{}', fullname='{}')>".format(
            self.username, self.fullname
        )

    def set_password(self, password):
        """
        Take the password given and hash it and commit the returned value in
        the database
        """
        self.password = hash_password(password)
        session.add(self)
        session.commit()

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return str(self.id)


# Define punch-tag relationship table
_punch_tags = Table(
    'punch_tags', Base.metadata,
    Column('punch_id', Integer, ForeignKey('punches.id')),
    Column('tags_id', Integer, ForeignKey('tags.id'))
)


class Punch(Base):

    __tablename__ = 'punches'

    id = Column(Integer, Sequence('punch_id_seq'), primary_key=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    description = Column(String(100))
    user_id = Column(ForeignKey('users.id'))
    tags = relationship(
        'Tag', secondary=_punch_tags, backref='punches'
    )

    def __repr__(self):
        return "<Punch(start='{}' end='{}', user={}')".format(
            self.start_time, self.end_time, self.user_id
        )


class Tag(Base):

    __tablename__ = 'tags'

    id = Column(Integer, Sequence('tag_id_seq'), primary_key=True)
    value = Column(String(50), nullable=False, unique=True)

    def __repr__(self):
        return "<Tag('{}')".format(self.value)
