This directory contains extended tests for the ``django_recommend.models`` package.

Tests are split up this way so users can run::

    python manage.py test django_recommend

to do some integration tests of django_recommend models against their database
backend, without needing to ship e.g. the ``quotes`` app to all users.
