@echo off
setlocal EnableDelayedExpansion
set "ROOT=%~dp0"
cd /d "%ROOT%"
set "PYTHONPATH=%CD%"
if exist ".venv\Scripts\python.exe" (set "PY=.venv\Scripts\python.exe") else (set "PY=python")
for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set D=%%a%%b%%c%%d
for /f "tokens=1-3 delims=:., " %%a in ("%time%") do set T=%%a%%b%%c
set "D=%D: =0%"
set "T=%T: =0%"
set "OUT=test_results\v056_%D%_%T%"
mkdir "%OUT%" >nul 2>nul
set EXITCODE=0

echo [1/3] Phase 35 corner Gaussian/UV bridge...
"%PY%" examples\phase35_corner_gaussian_uv_bridge.py > "%OUT%\phase35.log" 2>&1
set EC=!ERRORLEVEL!
type "%OUT%\phase35.log"
if not !EC!==0 set EXITCODE=!EC!

echo [2/3] Corner regression tests...
"%PY%" -m pytest -q tests\test_corner.py > "%OUT%\test_corner.log" 2>&1
set EC=!ERRORLEVEL!
type "%OUT%\test_corner.log"
if not !EC!==0 set EXITCODE=!EC!

echo [3/3] Version check...
"%PY%" -c "import qedcalc; print('QEDCalc',qedcalc.__version__)" > "%OUT%\version.log" 2>&1
type "%OUT%\version.log"
set EC=!ERRORLEVEL!
if not !EC!==0 set EXITCODE=!EC!

powershell -NoProfile -Command "Compress-Archive -Path '%OUT%\*' -DestinationPath '%OUT%.zip' -Force"
echo Result ZIP: %OUT%.zip
if !EXITCODE!==0 (echo v0.56 validation PASS) else (echo v0.56 validation FAIL ^(exit !EXITCODE!^))
exit /b !EXITCODE!
