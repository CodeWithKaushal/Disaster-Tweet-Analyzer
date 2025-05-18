@echo off
echo Running Django development server...
python manage.py collectstatic --noinput
python manage.py runserver
