@echo off
echo Resetting and starting White Raven Pourhouse...
echo.

echo Clearing Django cache...
python manage.py collectstatic --noinput --clear

echo Migrating database...
python manage.py migrate

echo Checking for issues...
python manage.py check

echo.
echo Starting development server...
echo Open your browser to: http://127.0.0.1:8000
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver
pause