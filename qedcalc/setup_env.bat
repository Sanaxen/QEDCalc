@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo QEDCalc virtual environment setup
echo ========================================

where py >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python launcher "py" was not found.
    echo Please install Python 3.11 or later with the Python launcher enabled.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creating virtual environment...
    py -m venv .venv
    if errorlevel 1 goto :error
) else (
    echo [1/3] Virtual environment already exists.
)

echo [2/3] Upgrading pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :error

echo [3/3] Installing required libraries...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo.
echo ========================================
echo Setup completed successfully.
echo QEDCalc itself is run directly from this folder.
echo No editable package build is required.
echo Run QEDCalc with run_qedcalc.bat

echo ========================================
pause
exit /b 0

:error
echo.
echo [ERROR] Setup failed.
echo If an old .venv is damaged, delete the .venv folder and run this batch again.
pause
exit /b 1
