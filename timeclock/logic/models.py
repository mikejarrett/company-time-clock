# -*- coding: utf-8 -*-

from sqlalchemy import (
    Column, DateTime, ForeignKey, Integer, Sequence, String, Table,
    UniqueConstraint, Float, Boolean
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

from .db import session, engine
from .utils import hash_password

Base = declarative_base()


class SerializeMixin(object):

    serializeable = []

    @property
    def serialize(self):
        return {
            field: getattr(self, field, '')
            for field in self.serializeable
        }


class User(Base, SerializeMixin):

    __tablename__ = 'users'
    serializeable = ['id', 'username', 'fullname', 'serialize_punches']

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    administrator = Column(Boolean, default=False)
    username = Column(String)
    fullname = Column(String)
    password = Column(String)
    punches = relationship('Punch', backref='user')

    UniqueConstraint('username', name='unque_username_constraint')

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

    @property
    def serialize_punches(self):
        return [punch.serialize for punch in self.punches.all()]


# Define punch-tag relationship table
_punch_tags = Table(
    'punch_tags', Base.metadata,
    Column('punch_id', Integer, ForeignKey('punches.id')),
    Column('tags_id', Integer, ForeignKey('tags.id'))
)


class Punch(Base, SerializeMixin):

    __tablename__ = 'punches'
    serializeable = [
        'id', 'start_time_string', 'end_time_string', 'description',
        'total_time', 'serialize_tags'
    ]


    id = Column(Integer, Sequence('punch_id_seq'), primary_key=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    description = Column(String(100))
    user_id = Column(ForeignKey('users.id'))
    total_time = Column(Float, default=0.0)
    tags = relationship(
        'Tag', secondary=_punch_tags, backref='punches'
    )

    def __repr__(self):
        return "<Punch(start='{}' end='{}', user={}')".format(
            self.start_time, self.end_time, self.user_id
        )

    @property
    def start_time_string(self):
        return self.start_time.isoformat()

    @property
    def end_time_string(self):
        return self.end_time.isoformat() if self.end_time else ''

    @property
    def serialize_tags(self):
        return [tag.serialize for tag in self.tags.all()]


class Tag(Base, SerializeMixin):

    __tablename__ = 'tags'
    serializeable = ['id', 'value']

    id = Column(Integer, Sequence('tag_id_seq'), primary_key=True)
    value = Column(String(50), nullable=False, unique=True)

    def __repr__(self):
        return "<Tag('{}')".format(self.value)
