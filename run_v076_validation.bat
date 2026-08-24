@echo off
setlocal
cd /d %~dp0
if exist ".venv\Scripts\python.exe" (set "PY=.venv\Scripts\python.exe") else (set "PY=python")
set "PYTHONPATH=%CD%"
echo QEDCalc v0.76 validation
"%PY%" run_phase65_corner_raw_radial_sign_ownership.py || exit /b 1
"%PY%" -m pytest -q tests/test_v076_corner_phase65.py || exit /b 1
"%PY%" -c "import qedcalc; print('QEDCalc',qedcalc.__version__)" || exit /b 1
echo v0.76 validation PASS
endlocal
