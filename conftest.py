from django.conf import settings


def pytest_configure():
    settings.configure(
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3'}},
        MIDDLEWARE_CLASSES=(),
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',

            'django_recommend'))
