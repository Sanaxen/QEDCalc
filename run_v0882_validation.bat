@echo off
setlocal
cd /d %~dp0
echo QEDCalc v0.88.2 validation
python examples\phase81_release_validation_stdlib.py
if errorlevel 1 exit /b 1
python -c "import importlib.util,sys; sys.exit(0 if importlib.util.find_spec('sympy') else 2)" >nul 2>&1
if errorlevel 2 goto nosympy
echo SymPy detected: running optional Phase-81 extended audit
set PYTHONPATH=%CD%
python examples\phase81_ordinary_ladder_end_to_end_checkpoint.py
if errorlevel 1 exit /b 1
goto done
:nosympy
echo SymPy not installed: optional extended symbolic audit SKIPPED
echo Standard-library release audit is sufficient for ZIP validation.
:done
echo v0.88.2 validation PASS
endlocal
