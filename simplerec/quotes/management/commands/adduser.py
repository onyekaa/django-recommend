"""Implementation of adduser manage.py command."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import getpass

from django.core.management import base
from django.contrib.auth import models


class Command(base.BaseCommand):
    """Add a normal user to the system with password '!'"""

    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument('username', help="The new user's username.")
        parser.add_argument('-p', '--password',
                            help="The new user's password.", default='!',
                            nargs='?')

    def handle(self, *_, **options):
        name = options['username']
        password = options['password']
        if not password:
            pass_1 = getpass.getpass('Enter password:')
            pass_2 = getpass.getpass('Enter password again:')
            if pass_1 != pass_2:
                self.stdout.write('Passwords do not match!')
                return
            password = pass_1

        email = '{}@example.com'.format(name)
        models.User.objects.create_user(name, email, password)
        self.stdout.write("User '{}' created.".format(name))
