django_recommend
================

.. image:: https://travis-ci.org/dan-passaro/django-recommend.svg
    :target: https://travis-ci.org/dan-passaro/django-recommend

Use ``pyrecommend`` in Django projects. 

**Warning:** not yet suitable for production.

``django_recommend/`` is the actual Django app intended for use in projects.

``simplerec/`` is a Django project used for testing.

**Important note:** Model classes/database schemas are only supported if they
have unique integer primary keys.


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



Notes
-----

There can be some potentially confusing behavior from this library if your
application involves objects that get deleted/deactivated. Currently I am not
sure how feasible it is to filter by a flag like 'deactivated'; tests for that
kind of functionality will be put into a future version.

If your data is ever deleted, by default, ``django_recommend`` will attempt to
delete all recommendation information about it at the next available chance.
This most notably can occur in ``ObjectSimilarityQueryset.get_instances_for``,
where you may, for example, have a queryset like::

    suggested_books = similar_books.order_by(
        '-score')[:5].get_instances_for(curr_book)

If one of the books that *would* be suggested for this book has since been
deleted, the default behavior will be to in fact give you a list of *four*
instances. This is because retrieving the deleted instances raises an
``ObjectDoesNotExist`` error in the Django ORM; the default behavior is to
simply delete that object's information from the recommendation data and skip
the object for now.

This can be controlled by the ``RECOMMEND_PURGE_MISSING_DATA`` boolean setting.
If this is ``False``, the exception will be propagated, so you may handle it in
a different way.
