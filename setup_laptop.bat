@echo off
echo Setting up White Raven Pourhouse on laptop...
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python from python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo.
echo Creating virtual environment...
python -m venv venv

echo.
echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Checking Django setup...
python manage.py check

echo.
echo Setup complete!
echo.
echo To start the website:
echo 1. Double-click 'start_server_8001.bat'
echo 2. OR run: python manage.py runserver 8001
echo 3. Then visit: http://127.0.0.1:8001
echo.
pause