# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

from collections import OrderedDict
from getpass import getpass
import argparse
import sys

from logic import controller as logic
from logic.utils import seconds_to_hours


class TimeClock(object):

    def __init__(self):
        self.punch_controller = logic.PunchController()
        self.user_controller = self.punch_controller.user_controller
        self.user = None
        self._running = False
        self._options_mapping = OrderedDict([
            ('I', ['punch_in', 'Punch In']),
            ('O', ['punch_out', 'Punch Out']),
            ('P', ['list_punches', 'List Punches']),
            ('C', ['create_user', 'Create User']),
            ('L', ['list_users', 'List users']),
            ('Q', ['quit', 'Quit']),
        ])

    def get_username(self):
        username = None
        try:
            while not username:
                username = raw_input('Username: ')
        except KeyboardInterrupt:
            return

        self.login(username)

    def login(self, username):
        password = None
        validated = False
        try:
            while not password or not validated:
                password = getpass()
                if password:
                    self.user, validated = \
                        self.user_controller.validate_username_and_password(
                            username, password
                        )
                if validated:
                    self._running = True
                    self.run()
        except KeyboardInterrupt:
            return

    def run(self):
        try:
            while self._running:
                event = self.menu().upper()
                if event == 'Q':
                    self._running = False

                option = self._options_mapping.get(event)
                if option and hasattr(self, option[0]):
                    getattr(self, option[0])()

        except KeyboardInterrupt:
            pass

        print('Goodbye!')

    def menu(self):
        print("\n")
        print("Time Clock Menu")
        print("===============")
        for key, options in self._options_mapping.iteritems():
            print('{0:^3} {1}'.format(key, options[1]))
        return raw_input('Please select an options: ')

    def punch_in(self):
        description = None
        while not description:
            description = raw_input('Description: ')

        tags = raw_input(
            'Enter tags as comma seperated values (enter for none): '
        )
        tags = tags.split(',')

        punch = self.punch_controller.punch_in(
            self.user.id, description, tags=tags, user=self.user
        )
        if punch:
            print('Punched in at: {}'.format(punch.start_time))
        else:
            print('Oops... Something went wrong.')

    def punch_out(self):
        punch = self.punch_controller.punch_out(self.user.id, self.user)
        if punch:
            print('Punched out at: {}'.format(punch.end_time))
        else:
            print(
                "Oops... We couldn't find an incomplete punch or something "
                "went wrong."
            )

    def list_punches(self):
        header = '{0:40} {1:26}\t{2:25}\t{3:6}'.format(
            'Description', 'Punch In', 'Punch Out', 'Total'
        )
        print(header)
        print('=' * len(header))

        for punch in self.user.punches:

            print('{0:40} {1}\t{2}\t{3:2.3f}'.format(
                punch.description[:40], punch.start_time, punch.end_time,
                punch.total_time
            ))

    def create_user(self):
        username = None
        while not username:
            username = raw_input('Username: ')

        fullname = None
        while not fullname:
            fullname = raw_input('Full Name: ')

        password = None
        password1 = ''
        while not (password or password1) or password != password1:
            password = getpass()
            password1 = getpass('Re-enter password: ')

        self.user_controller.create_user(username, fullname, password)

    def list_users(self):
        formatter = '{0:20}\t{1:50}'
        header = formatter.format('Username', 'Full Name')
        print(header)
        print("=" * len(header))
        for user in self.user_controller.get_users():
            if user.username is None:
                print(formatter.format(user.username, ''))

            print(formatter.format(user.username, user.fullname))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Time Clock Tracker.')
    parser.add_argument(
        '-u', '--username', metavar='USER', type=str, nargs='?', default=None,
        help='username to login the system'
    )

    args = parser.parse_args()
    timeclock = TimeClock()
    if args.username:
        timeclock.login(args.username)
    else:
        timeclock.get_username()
    sys.exit()
