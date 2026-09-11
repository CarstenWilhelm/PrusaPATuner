@echo off
rem One-click launcher: creates the venv on first run, then starts the app.
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    where py >nul 2>&1 || (
        echo Python not found. Install Python 3.11+ from https://python.org
        echo Tick "Add python.exe to PATH" in the installer.
        pause
        exit /b 1
    )
    echo First run - creating .venv and installing dependencies...
    py -3 -m venv .venv || goto :fail
    .venv\Scripts\python.exe -m pip install --upgrade pip || goto :fail
    .venv\Scripts\python.exe -m pip install -e . || goto :fail
)

.venv\Scripts\python.exe -m prusa_pa_tuner %* || goto :fail
exit /b 0

:fail
echo.
echo Startup failed - see the error above.
pause
exit /b 1
