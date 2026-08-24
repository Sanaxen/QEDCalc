@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist ".venv\Scripts\python.exe" (set "PY=.venv\Scripts\python.exe") else (set "PY=python")

for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "STAMP=%%I"
set "OUTROOT=test_results"
set "OUTDIR=%OUTROOT%\v052_%STAMP%"
set "LOG=%OUTDIR%\validation.log"
set "ZIP=%OUTROOT%\v052_%STAMP%.zip"

if not exist "%OUTROOT%" mkdir "%OUTROOT%"
mkdir "%OUTDIR%"

echo QEDCalc v0.52 validation > "%LOG%"
echo Started: %DATE% %TIME% >> "%LOG%"
echo Working directory: %CD% >> "%LOG%"
echo. >> "%LOG%"

call :run "[1/4] Phase 27 vacuum polarization" examples\phase27_vacuum_polarization_raw_to_final.py
if errorlevel 1 goto :failed

call :run "[2/4] Phase 28 self-energy downstream" examples\phase28_self_energy_analytic_downstream.py
if errorlevel 1 goto :failed

call :pytest "[3/4] Focused v0.52 tests" tests\test_v052_vacuum_polarization_raw_to_final.py tests\test_v052_self_energy_analytic_downstream.py
if errorlevel 1 goto :failed

call :pytest "[4/4] Existing VP/self-energy regression" tests\test_vacuum_polarization.py tests\test_v021_bare_diagram.py tests\test_self_energy.py tests\test_v022_self_energy_raw.py
if errorlevel 1 goto :failed

echo.>> "%LOG%"
echo v0.52 validation PASS>> "%LOG%"
echo Exit code: 0>> "%LOG%"
echo v0.52 validation PASS
set "RC=0"
goto :package

:run
set "LABEL=%~1"
set "SCRIPT=%~2"
echo %LABEL%...
echo %LABEL%...>> "%LOG%"
"%PY%" "%SCRIPT%" >> "%LOG%" 2>&1
set "RC=%ERRORLEVEL%"
type "%LOG%" | powershell -NoProfile -Command "$input | Select-Object -Last 25"
exit /b %RC%

:pytest
set "LABEL=%~1"
shift
echo %LABEL%...
echo %LABEL%...>> "%LOG%"
"%PY%" -m pytest -q %* >> "%LOG%" 2>&1
set "RC=%ERRORLEVEL%"
type "%LOG%" | powershell -NoProfile -Command "$input | Select-Object -Last 25"
exit /b %RC%

:failed
set "RC=%ERRORLEVEL%"
echo.>> "%LOG%"
echo v0.52 validation FAILED>> "%LOG%"
echo Exit code: %RC%>> "%LOG%"
echo v0.52 validation FAILED. Exit code: %RC%

:package
"%PY%" --version > "%OUTDIR%\python_version.txt" 2>&1
"%PY%" -c "import sympy, pytest; print('SymPy', sympy.__version__); print('pytest', pytest.__version__)" > "%OUTDIR%\package_versions.txt" 2>&1
copy /y "%LOG%" "%OUTDIR%\validation.log" >nul

echo %RC%> "%OUTDIR%\exit_code.txt"
powershell -NoProfile -Command "Compress-Archive -Path '%OUTDIR%\*' -DestinationPath '%ZIP%' -Force"

echo.
echo Result ZIP:
echo %CD%\%ZIP%
endlocal & exit /b %RC%
