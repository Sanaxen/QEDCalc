@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
set "PY=.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"
if not exist test_results mkdir test_results
for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set DS=%%a%%b%%c%%d
for /f "tokens=1-3 delims=:., " %%a in ("%time%") do set TS=%%a%%b%%c
set "OUT=test_results\v053_%DS%_%TS%"
mkdir "%OUT%" >nul 2>&1

echo [1/3] Phase 29 raw self-energy bare bridge...
"%PY%" examples\phase29_self_energy_raw_bare_bridge.py > "%OUT%\phase29.log" 2>&1
if errorlevel 1 goto fail

echo [2/3] Phase 28 downstream regression...
"%PY%" examples\phase28_self_energy_analytic_downstream.py > "%OUT%\phase28.log" 2>&1
if errorlevel 1 goto fail

echo [3/3] Focused self-energy tests...
"%PY%" -m pytest -q tests\test_self_energy.py::test_v053_raw_self_energy_pair_reconstructs_bare_parametric_checkpoints tests\test_self_energy.py::test_v053_raw_self_energy_denominator_polynomials_are_generated tests\test_self_energy.py::test_v053_raw_self_energy_uv_subsector_is_regenerated tests\test_v022_self_energy_raw.py > "%OUT%\pytest.log" 2>&1
if errorlevel 1 goto fail

echo 0>"%OUT%\exit_code.txt"
powershell -NoProfile -Command "Compress-Archive -Path '%OUT%\*' -DestinationPath '%OUT%.zip' -Force" >nul
 echo v0.53 validation PASS
 echo Result: %OUT%.zip
 exit /b 0
:fail
set EC=%ERRORLEVEL%
echo %EC%>"%OUT%\exit_code.txt"
powershell -NoProfile -Command "Compress-Archive -Path '%OUT%\*' -DestinationPath '%OUT%.zip' -Force" >nul
 echo v0.53 validation FAIL. Exit code: %EC%
 echo Result: %OUT%.zip
 exit /b %EC%
