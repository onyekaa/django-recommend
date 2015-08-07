"""Quote-specific manage.py commands."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from django.core.management import base

from ... import models


class Command(base.BaseCommand):
    """Clear all suggestion data and views/favorites."""

    def add_arguments(self, parser):
        parser.add_argument('--dry-run',
                            action='store_true',
                            dest='dry_run',
                            default=False,
                            help="Do not actually delete any data.")

    def handle(self, *args, **options):  # pylint: disable=unused-argument
        classes = [models.ViewedQuote, models.FavoriteQuote,
                   models.AnonymousViewedQuote, models.QuoteSimilarity]

        if not options['dry_run']:
            self.stdout.write('Deleting:')
        else:
            self.stdout.write('Would delete:')

        for cls in classes:
            count = cls.objects.count()
            msg = '{} {} objects.'.format(count, cls.__name__)
            self.stdout.write(msg)
            if not options['dry_run']:
                cls.objects.all().delete()
Command.help = Command.__doc__
