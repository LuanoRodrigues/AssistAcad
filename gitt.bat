@echo off

REM Change to the project directory
cd /d "C:\Users\luano\Downloads\AcAssitant" || exit /b

REM Add all changes to git
git add .

REM Commit the changes with a message
git commit -m "desktop"

REM Push the changes to the remote repository
git push origin main

REM Check if the push was successful
IF %ERRORLEVEL% EQU 0 (
    echo Changes pushed to GitHub successfully.
    pause
) ELSE (
    echo There was an error pushing changes to GitHub.
)

REM Wait for user input before closing
echo Press any key to close...
pause >nul
