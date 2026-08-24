@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Virtual environment is not installed yet.
    echo Running setup_env.bat first...
    call setup_env.bat
    if errorlevel 1 exit /b 1
)

if not exist "output" mkdir "output"

echo ========================================
echo QEDCalc - 1-loop vertex symbolic workflow

echo ========================================
".venv\Scripts\python.exe" -m examples.vertex_1loop_stage5

echo.
echo Output Markdown:
echo   output\vertex_1loop_session.md
echo.
echo ========================================
echo Finished.
echo ========================================
pause
