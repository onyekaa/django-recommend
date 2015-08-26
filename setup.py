"""setuptools config for django-recommend."""
import os
from setuptools import setup


def read(fname):
    """Get the contents of the named file as a string."""
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return u''


setup(
    name='django-recommend',
    version='0.1.dev6',
    author='Dan Passaro',
    author_email='danpassaro@gmail.com',
    description='Generate recommendations in Django.',
    license='MIT',
    url='https://github.com/dan-passaro/django-recommend',
    long_description=read('README.rst'),

    package_dir={'': 'src'},
    packages=['django_recommend', 'django_recommend.templatetags'],
    install_requires=['django', 'pyrecommend'],
    setup_requires=['wheel'],
)
