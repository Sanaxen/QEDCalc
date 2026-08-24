@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist ".venv\Scripts\python.exe" (set "PY=.venv\Scripts\python.exe") else (set "PY=python")

echo [1/4] Phase 27 vacuum polarization...
%PY% examples\phase27_vacuum_polarization_raw_to_final.py || exit /b 1

echo [2/4] Phase 28 self-energy downstream...
%PY% examples\phase28_self_energy_analytic_downstream.py || exit /b 1

echo [3/4] Focused v0.52 tests...
%PY% -m pytest -q tests\test_v052_vacuum_polarization_raw_to_final.py tests\test_v052_self_energy_analytic_downstream.py || exit /b 1

echo [4/4] Existing VP/self-energy regression...
%PY% -m pytest -q tests\test_vacuum_polarization.py tests\test_v021_bare_diagram.py tests\test_self_energy.py tests\test_v022_self_energy_raw.py || exit /b 1

echo v0.52 validation PASS
endlocal
