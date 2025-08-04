@echo off
echo =================================
echo   White Raven Pourhouse
echo   Auto Git Push Script
echo =================================
echo.

echo Checking for changes...
git status --porcelain > temp_status.txt
if %errorlevel% neq 0 (
    echo ERROR: Git status failed!
    pause
    exit /b 1
)

for /f %%i in (temp_status.txt) do set changes=%%i
del temp_status.txt

if "%changes%"=="" (
    echo No changes to commit.
    echo Repository is up to date.
    timeout /t 3 /nobreak > nul
    exit /b 0
)

echo Adding all changes...
git add .
if %errorlevel% neq 0 (
    echo ERROR: Git add failed!
    pause
    exit /b 1
)

echo.
echo Creating commit with auto-generated message...
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a:%%b)

git commit -m "Auto commit - %mydate% %mytime%

Updates and improvements to White Raven Pourhouse website.

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

if %errorlevel% neq 0 (
    echo ERROR: Git commit failed!
    pause
    exit /b 1
)

echo.
echo Pushing to GitHub...
git push
if %errorlevel% neq 0 (
    echo ERROR: Git push failed!
    echo Check your internet connection and GitHub credentials.
    pause
    exit /b 1
)

echo.
echo SUCCESS! Changes pushed to GitHub.
echo You can now clone/pull on your laptop.
echo.
timeout /t 3 /nobreak > nul