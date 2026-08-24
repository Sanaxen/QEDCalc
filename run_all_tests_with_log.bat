@echo off
setlocal EnableExtensions
cd /d "%~dp0"

rem ============================================================
rem QEDCalc full regression test runner with persistent logs
rem ============================================================

if not exist "test_results" mkdir "test_results"

for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "STAMP=%%I"
set "RUNDIR=test_results\full_test_%STAMP%"
mkdir "%RUNDIR%"

set "LOG=%RUNDIR%\pytest_full.log"
set "ENVLOG=%RUNDIR%\environment.txt"
set "SUMMARY=%RUNDIR%\summary.txt"
set "ZIP=test_results\full_test_%STAMP%.zip"

echo ============================================================
echo QEDCalc full test run
echo Results: %RUNDIR%
echo ============================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [INFO] .venv was not found. Running setup_env.bat first...
    call setup_env.bat
    if errorlevel 1 (
        echo [ERROR] setup_env.bat failed.
        echo setup_failed=1>"%SUMMARY%"
        goto :package
    )
)

rem ---- Environment information --------------------------------
(
    echo QEDCalc full regression test environment
    echo Timestamp: %STAMP%
    echo Working directory: %CD%
    echo.
    echo [Python]
    ".venv\Scripts\python.exe" --version
    echo.
    echo [Python executable]
    ".venv\Scripts\python.exe" -c "import sys; print(sys.executable); print(sys.version)"
    echo.
    echo [Platform]
    ".venv\Scripts\python.exe" -c "import platform; print(platform.platform()); print(platform.machine())"
    echo.
    echo [SymPy / pytest]
    ".venv\Scripts\python.exe" -c "import sympy, pytest; print('sympy=' + sympy.__version__); print('pytest=' + pytest.__version__)"
    echo.
    echo [Installed packages]
    ".venv\Scripts\python.exe" -m pip freeze
) > "%ENVLOG%" 2>&1

rem ---- Full pytest run -----------------------------------------
echo [INFO] Starting full pytest suite.
echo [INFO] This may run for a long time. The log is written continuously to:
echo        %LOG%
echo.

(
    echo ============================================================
    echo QEDCalc FULL PYTEST RUN
    echo Timestamp: %STAMP%
    echo ============================================================
    echo.
) > "%LOG%"

".venv\Scripts\python.exe" -m pytest -vv --durations=100 >> "%LOG%" 2>&1
set "RC=%ERRORLEVEL%"

(
    echo exit_code=%RC%
    echo timestamp=%STAMP%
    echo log=%LOG%
    echo environment=%ENVLOG%
) > "%SUMMARY%"

if "%RC%"=="0" (
    echo.
    echo [PASS] All tests passed.
) else (
    echo.
    echo [FAIL] pytest returned exit code %RC%.
    echo        Please send the generated ZIP back for analysis.
)

:package
rem ---- Package result files ------------------------------------
if exist "%ZIP%" del /q "%ZIP%" >nul 2>&1
powershell -NoProfile -Command "Compress-Archive -Path '%RUNDIR%\*' -DestinationPath '%ZIP%' -Force" >nul 2>&1

if exist "%ZIP%" (
    echo.
    echo ============================================================
    echo Result package created:
    echo %ZIP%
    echo ============================================================
    echo Please send this ZIP back to ChatGPT.
) else (
    echo.
    echo [WARN] Could not create ZIP automatically.
    echo Please send the folder below instead:
    echo %RUNDIR%
)

echo.
pause

if defined RC exit /b %RC%
exit /b 1
