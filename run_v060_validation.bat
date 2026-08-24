@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d %~dp0
set PYTHONPATH=%CD%
for /f "tokens=1-4 delims=/ " %%a in ("%date%") do set D=%%a%%b%%c%%d
set T=%time: =0%
set T=%T::=%
set T=%T:.=%
set OUT=test_results\v060_%D%_%T%
mkdir "%OUT%" >nul 2>nul
python -c "import qedcalc; print(qedcalc.__version__)" > "%OUT%\version.txt" 2>&1
python -c "from qedcalc.operations.corner import *; s=corner_outer_projector_streams(); print('Phase-39 corner finite-inner -> outer projector streams'); print('term counts:',s.term_counts); r=corner_outer_stream_denominator_residuals(); print('denominator residuals:',r); assert all(x==0 for x in r.values()); print('Phase-39: PASS')" > "%OUT%\phase39.log" 2>&1
if errorlevel 1 goto :fail
python -m pytest -q tests\test_corner.py > "%OUT%\corner_tests.log" 2>&1
if errorlevel 1 goto :fail
> "%OUT%\summary.txt" echo v0.60 validation PASS
>> "%OUT%\summary.txt" echo Expected version: 0.60.0
powershell -NoProfile -Command "Compress-Archive -Path '%OUT%\*' -DestinationPath '%OUT%.zip' -Force"
echo v0.60 validation PASS
echo Result ZIP: %OUT%.zip
exit /b 0
:fail
> "%OUT%\summary.txt" echo v0.60 validation FAIL
powershell -NoProfile -Command "Compress-Archive -Path '%OUT%\*' -DestinationPath '%OUT%.zip' -Force"
echo v0.60 validation FAIL
exit /b 1
