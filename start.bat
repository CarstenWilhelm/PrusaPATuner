@echo off
rem One-click launcher: creates the venv on first run, then starts the app.
cd /d "%~dp0"

rem Probe the package, not just the venv folder: an install interrupted partway
rem leaves a python.exe behind, and a folder check would skip the repair.
set NEEDS_INSTALL=1
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe -c "import prusa_pa_tuner" >nul 2>&1 && set NEEDS_INSTALL=0
)

if "%NEEDS_INSTALL%"=="1" (
    where py >nul 2>&1 || goto :nopython
    echo Setting up - creating .venv and installing dependencies...
    if not exist ".venv\Scripts\python.exe" ( py -3 -m venv .venv || goto :fail )
    .venv\Scripts\python.exe -m pip install --upgrade pip || goto :fail
    .venv\Scripts\python.exe -m pip install -e . || goto :fail
)

rem Uvicorn exits 3 both on a clean Ctrl-C and on a startup failure such as a
rem busy port, so the exit code cannot tell the two apart. Rather than guess,
rem say something true in either case and keep the window open to read it.
.venv\Scripts\python.exe -m prusa_pa_tuner %*
set RC=%ERRORLEVEL%
if %RC%==0 exit /b 0
echo.
echo Server stopped (exit %RC%). If that was not deliberate, the reason is above.
pause
exit /b %RC%

:nopython
echo Python not found. Install Python 3.11+ from https://python.org
echo Tick "Add python.exe to PATH" in the installer.
pause
exit /b 1

:fail
echo.
echo Startup failed - see the error above.
pause
exit /b 1
