@echo off
chcp 65001
echo ========================================================
echo  SAMWAY AI APP - AUTOMATIC GITHUB UPLOADER
echo ========================================================
echo.
echo 1. Make sure you have created a repository on GitHub.
echo 2. If prompted for login, use your GitHub account.
echo.

set /p REPO_URL="Paste your GitHub Repository URL here (e.g. https://github.com/Start/char-app.git): "

if "%REPO_URL%"=="" (
    echo Error: URL is empty.
    pause
    exit /b
)

echo.
echo Initializing Git...
git init
git branch -M main

echo.
echo Adding files (ignoring large/secret files)...
git add .

echo.
echo Committing changes...
git commit -m "Initial upload for deployment"

echo.
echo Connecting to GitHub...
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo.
echo Pushing to GitHub...
git push -u origin main

echo.
echo ========================================================
if %errorlevel% neq 0 (
    echo [ERROR] Upload failed. Please check the error message above.
    echo Common issues:
    echo  - URL is incorrect
    echo  - Folder is already connected to another repo
    echo  - Login failed
) else (
    echo [SUCCESS] Upload complete!
    echo Now go to Streamlit Community Cloud and connect this repo.
)
echo ========================================================
pause
