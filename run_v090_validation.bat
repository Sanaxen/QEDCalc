@echo off
setlocal
cd /d %~dp0
echo QEDCalc v0.90 validation
python examples\phase83_two_loop_completion_regression_stdlib.py
if errorlevel 1 exit /b 1
python -c "import sympy" >nul 2>nul
if errorlevel 1 goto NOSYMPY
echo SymPy detected: running optional scientific regression...
set PYTHONPATH=%CD%
python examples\phase83_two_loop_extended_scientific_regression.py
if errorlevel 1 exit /b 1
goto DONE
:NOSYMPY
echo SymPy not installed: optional scientific regression SKIPPED
echo Standard-library complete two-loop regression is sufficient for ZIP validation.
:DONE
echo v0.90 validation PASS
endlocal
