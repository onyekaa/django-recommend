# coding: utf-8
"""Script to upload to PyPI and tag in git."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import errno
import glob
import os.path
import shutil
import subprocess
import sys


PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))


def git(*args):
    """Shorthand for executing git commands in a subprocess.

    E.g.::

        git('checkout', 'stable')

    Would checkout the branch ``stable``.

    """
    subprocess.check_call(['git', '-C', PROJECT_DIR] + list(args))


def push_to_github():
    """Make sure latest code is on github."""
    git('push')


def path_to(*parts):
    """Get an absolute path to a file/folder in the project."""
    return os.path.join(PROJECT_DIR, *parts)


def rmdir_if_exists(path):
    """Remove path if it exists."""
    try:
        shutil.rmtree(path)
    except OSError as exc:
        if exc.errno == errno.ENOENT:  # File does not exist
            pass
        else:
            raise


def clean_build_dirs():
    """Remove old build artifacts."""
    rmdir_if_exists(path_to('build'))
    rmdir_if_exists(path_to('dist'))


def build_package():
    """Build a source and binary wheel package."""
    subprocess.check_call([sys.executable, path_to('setup.py'),
                           'sdist', 'bdist_wheel'])


def upload_with_twine():
    """Upload to pypi.python.org using twine."""
    files = glob.glob(path_to('dist', '*'))
    subprocess.check_call([sys.executable, '-m', 'twine', 'upload'] + files)


def tag_git_commit_with_version():
    """Tag the latest git commit with the current package version."""
    current_version = subprocess.check_output([
        sys.executable, path_to('setup.py'), '-V']).strip()
    tag_str = 'v{}'.format(current_version)
    print('Tagging', tag_str, 'in git')
    git('tag', tag_str)
    git('push', 'origin', tag_str)


if __name__ == '__main__':
    push_to_github()
    clean_build_dirs()
    build_package()
    upload_with_twine()
    tag_git_commit_with_version()
