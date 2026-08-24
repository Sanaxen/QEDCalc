@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist ".venv\Scripts\python.exe" (set "PY=.venv\Scripts\python.exe") else (set "PY=python")
for /f "tokens=1-4 delims=/ " %%a in ("%date%") do set D=%%a%%b%%c%%d
set T=%time: =0%
set T=%T::=%
set T=%T:.=%
set OUT=test_results\v061_%D%_%T%
mkdir "%OUT%" >nul 2>nul
"%PY%" -c "import qedcalc; print(qedcalc.__version__)" > "%OUT%\version.txt" 2>&1
"%PY%" examples\phase42_corner_physical_inner_outer_bridge.py > "%OUT%\phase42.log" 2>&1
if errorlevel 1 goto :fail
"%PY%" -m pytest -q tests\test_corner.py > "%OUT%\corner_tests.log" 2>&1
if errorlevel 1 goto :fail
> "%OUT%\summary.txt" echo v0.61 validation PASS
>> "%OUT%\summary.txt" echo Expected version: 0.61.0
powershell -NoProfile -Command "Compress-Archive -Path '%OUT%\*' -DestinationPath '%OUT%.zip' -Force"
echo v0.61 validation PASS
echo Result ZIP: %OUT%.zip
exit /b 0
:fail
> "%OUT%\summary.txt" echo v0.61 validation FAIL
powershell -NoProfile -Command "Compress-Archive -Path '%OUT%\*' -DestinationPath '%OUT%.zip' -Force"
echo v0.61 validation FAIL
exit /b 1
