#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Classes that control the "punching in" and "punching out" to keep track of
time, tasks and thing else that needs to be tracked via time
"""

from datetime import datetime, timedelta

from sqlalchemy import or_
from sqlalchemy.orm import sessionmaker

from .db import engine
from .excepts import DoesNotExist
from .models import User, Punch, Tag
from .utils import validate_password, time_difference_in_hours


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

    def __init__(self, session=None):
        """ Init super on BaseController and initialize a user controller and
        set it to `user_controller`
        """
        super(PunchController, self).__init__(session)
        self.user_controller = UserController(self.session)

    def punch_in(self, user_id, description, tags=(), user=None):
        """ Adds a new punch entry for the user and if there is an old punch
        entry that does not have a `end_time` use the same time as the
        start_time` of this new punch.

        Args:
            user_id: The user id that this punch will be associated with
            description: A description of the activity that is being worked on
            tags: A list of tags that will be associated with this punch
            user: Option user object to help reduce the calls to the DB

        Returns:
            punch: Returns the punch that was created

        Raises:
            None
        """
        now = datetime.now()
        if not user:
            user = self.user_controller.get_user_by_id(user_id)
        if not user:
            # TODO Add some logging here, maybe change the flow
            return

        self._end_last_punch(user, now)
        tags = self._get_or_create_tags(tags)

        punch = Punch(
            start_time=now, description=description, tags=tags, user=user

        )
        self.session.add(punch)
        self.session.commit()
        return punch

    def punch_out(self, user_id, user=None):
        """ Set the `end_time` for the most recent `start_time` punch of the
        user provided by the `user_id`

        Args:
            user_id: The user id that this punch will be associated with
            user: Option user object to help reduce the calls to the DB

        Returns:
            punch: Returns the punch that was updated

        Raises:
            None
        """
        now = datetime.now()
        if not user:
            user = self.user_controller.get_user_by_id(user_id)
        if not user:
            # TODO Add some logging here, maybe change the flow
            return

        punch = self._end_last_punch(user, now)
        self.session.commit()
        return punch

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
            punch.total_time = time_difference_in_hours(
                punch.start_time, end_time
            )
            self.session.add(punch)
        return punch

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
            tag = tag.lower()
            instance = self.session.query(Tag).filter_by(value=tag).first()
            if instance:
                new_tags.append(instance)
            else:
                instance = Tag(value=tag)
                self.session.add(instance)
                new_tags.append(instance)
        return new_tags

    def get_user_punches_by_range(self, user, start=None, end=None):
        """ Retrieve all punches for a specific User object filtering by start
        and end time.
        If end is not provided set it to now
        If start is not provided set now minus 14 daus

        Args:
            user: User object
            start: datetime object
            end: datetime object

        Returns:
            Query of punches in that range

        Raises:
            None
        """
        if not end:
            end = datetime.now()

        if not start:
            start = end - timedelta(days=14)

        return self.session.query(Punch).filter_by(user=user).filter(
            Punch.start_time>=start
        ).filter(or_(
            Punch.end_time<=end, Punch.end_time==None
        )).order_by(Punch.start_time)


class UserController(BaseController):

    def validate_username_and_password(self, username, password):
        """ Valid the username and password against what is stored in the
        database

        Args:
            username: string username
            password: string of password

        Returns:
            user: a user object or None
            validated: boolean if validated or not

        Raises:
            None
        """
        user = self.get_user(username)
        if user:
            validated = validate_password(password, user.password)
        else:
            validated = False
        return user, validated

    def get_user(self, username):
        """ Retrieve the user by username

        Args:
            username: string username

        Returns:
            user: User object

        Raises:
            None
        """
        return self.session.query(User).filter_by(username=username).first()

    def get_user_by_id(self, user_id):
        """ Attempts to retrieve the user from the database by id

        Args:
            user_id: The user id that of the user we want

        Returns:
            user: User object or none

        Raises:
            None
        """
        return self.session.query(User).get(user_id)

    def get_user_by_username(self, username):
        """ Attempts to retrieve the user from the database by username

        Args:
            username: The username that of the user we want

        Returns:
            user: User object or none

        Raises:
            None
        """
        return self.session.query(User).filter_by(username=username).first()

    def get_users(self):
        """ Get all users in the db

        Args:
            None

        Returns:
            All users in the db

        Raises:
            None
        """
        return self.session.query(User).all()

    def create_user(self, username, fullname, password):
        """ Create a user in the db and store password securely

        Args:
            username: string username
            fullname: string fullname
            password: string password

        Returns:
            None

        Raises:
            None
        """
        user = User(username=username.lower(), fullname=fullname)
        user.set_password(password)
