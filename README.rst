django_recommend
================

.. image:: https://travis-ci.org/dan-passaro/django-recommend.svg
    :target: https://travis-ci.org/dan-passaro/django-recommend

Use ``pyrecommend`` in Django projects. 

**Warning:** not yet suitable for production.

``django_recommend/`` is the actual Django app intended for use in projects.

``simplerec/`` is a Django project used for testing.


Quickstart
----------

* Add ``django_recommend`` to your ``INSTALLED_APPS``, and run
  ``python manage.py migrate``.

* Set ``SESSION_SAVE_EVERY_REQUEST=True`` in your settings, to ensure anonymous
  users can be tracked.

* In your views, call ``django_recommend.set_score(request, object, score)`` to
  start recording user scores. (Currently this is assumed to be implicit
  feedback.) **Note:** This will use session keys to store scores for users who
  aren't authenticated.

* In your templates, use ``{% load django_recommend %}`` and
  ``{{ obj|similar_objects }}`` to show similar objects to visitors. This
  filter returns a list, so you may also do, for example:

  .. code:: html+django

      {% load django_recommend %}
      {% with similar_products as product|similar_objects %}
          {% if similiar_products %}
              <h2>Other users also liked:</h2>
              <ul>
              {% for product in similar_products %}
                  <li><a href="{{ product.get_absolute_url }}">{{ product }}</a></li>
              {% endfor %}
              </ul>
          {% endif %}
      {% endwith %}
