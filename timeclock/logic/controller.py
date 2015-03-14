#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Classes that control the "punching in" and "punching out" to keep track of
time, tasks and thing else that needs to be tracked via time
"""

from datetime import datetime

from sqlalchemy.orm import sessionmaker

from .db import engine
from .excepts import DoesNotExist
from .models import User, Punch, Tag
from .utils import validate_password


class BaseController(object):

    def __init__(self, session=None):
        """ Initialize the punch controller object, if a sesssion is not
        provided instatied one. Assign session to `self.session`
        """
        if not session:
            session_maker = sessionmaker(bind=engine)
            session = session_maker()
        self.session = session


class PunchController(BaseController):
    """ Controller class that handles the punching in and out for users """

    def punch_in(self, user_id, description, tags=()):
        """ Adds a new punch entry for the user and if there is an old punch
        entry that does not have a `end_time` use the same time as the
        start_time` of this new punch.

        Args:
            user_id: The user id that this punch will be associated with
            description: A description of the activity that is being worked on
            tags: A list of tags that will be associated with this punch

        Returns:
            None

        Raises:
            DoesNotExist is user not found in the databse
        """
        now = datetime.now()
        user = self._get_user(user_id)
        self._end_last_punch(user, now)
        tags = self._get_or_create_tags(tags)

        punch = Punch(
            start_time=now, description=description, tags=tags, user=user

        )
        self.session.add(punch)
        self.session.commit()

    def punch_out(self, user_id):
        """ Set the `end_time` for the most recent `start_time` punch of the
        user provided by the `user_id`

        Args:
            user_id: The user id that this punch will be associated with

        Returns:
            None

        Raises:
            None
        """
        now = datetime.now()
        user = self._get_user(user_id)
        self._end_last_punch(user, now)
        self.session.commit()

    def _get_user(self, user_id):
        """ Attempts to retrieve the user from the database by id if it nothing
        is returned raise DoesNotExist

        Args:
            user_id: The user id that of the user we want

        Returns:
            user

        Raises:
            DoesNotExist is user not found in the databse
        """
        user = self.session.query(User).get(user_id)
        if not user:
            raise DoesNotExist(
                'User with id {} was not found in the database'.format(user_id)
            )
        return user

    def _end_last_punch(self, user, end_time):
        """ Retrieve the last user punch that does not have and end time

        Args:
            user: user object
            end_time: python datetime object

        Returns:
            None

        Raises:
            None
        """
        punch_query = \
            self.session.query(Punch).filter_by(user_id=user.id, end_time=None)
        punch = punch_query.first()
        if punch:
            punch.end_time = end_time
            self.session.add(punch)

    def _get_or_create_tags(self, tags):
        """ Loop through iterable of tags and get them if they are in the
        database or create them if they are not in the database

        Args:
            tags: Iterable of strings containing tags

        Returns:
            new_tags: List of either new tags or tags from the DB

        Raises:
            TypeError if tags is a non-iterable type
        """
        # We want to raise an exception if tag type isn't iterable
        tags = iter(tags)

        new_tags = []
        for tag in tags:
            instance = self.session.query(Tag).filter_by(value=tag).first()
            if instance:
                new_tags.append(instance)
            else:
                instance = Tag(value=tag)
                self.session.add(instance)
                new_tags.append(instance)
        return new_tags


class UserController(BaseController):

    def validate_username_and_password(self, username, password):
        user = self.get_user(username)
        if user:
            validated = validate_password(password, user.password)
        else:
            validated = False

        return user, validated

    def get_user(self, username):
        return self.session.query(User).filter_by(username=username).first()

    def get_user_by_id(self, user_id):
        return self.session.query(User).filter_by(user_id=user_id).first()
