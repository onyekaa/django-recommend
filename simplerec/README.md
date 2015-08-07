A simple Django project to try and leverage the recommendation calculations.

Note: you must have `bower` installed and on your path.

To get going, run:

    pip install -r requirements.txt
    python manage.py migrate
    python manage.py bower install

You may also want to create some users. You may also load sample quotes with

    python manage.py loaddata sample_quotes
