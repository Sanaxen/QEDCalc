@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist ".venv\Scripts\python.exe" (
  set "PY=.venv\Scripts\python.exe"
) else (
  set "PY=python"
)

echo === QEDCalc v0.70 validation ===
%PY% examples\phase55_corner_local_finite_ownership.py || exit /b 1
%PY% examples\phase56_corner_sequential_normalization_ownership.py || exit /b 1

echo === corner regression: phases before 50 ===
%PY% -m pytest -q tests\test_corner.py -k "not phase50 and not phase51 and not phase52 and not phase53 and not phase54 and not phase55 and not phase56" || exit /b 1

echo === corner regression: phases 50-56 ===
%PY% -m pytest -q tests\test_corner.py -k "phase50 or phase51 or phase52 or phase53 or phase54 or phase55 or phase56" || exit /b 1

echo === version ===
%PY% -c "import qedcalc; print(qedcalc.__version__)" || exit /b 1

echo v0.70 validation PASS
endlocal
