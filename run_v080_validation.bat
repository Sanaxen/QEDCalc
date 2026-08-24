@echo off
setlocal
cd /d "%~dp0"
echo QEDCalc v0.80 validation
if exist ".venv\Scripts\python.exe" (
  set "PY=.venv\Scripts\python.exe"
) else (
  set "PY=python"
)
set "PYTHONPATH=%CD%"
"%PY%" -c "from qedcalc.operations.corner import corner_phase73_finite_rho_cancellation_wick_audit as f; a=f(); assert a['electron_scalar_cancellation_residual']==0 and a['photon_scalar_cancellation_residual']==0; print('Phase-73 cancellation/Wick audit PASS')" || goto :fail
"%PY%" -m pytest -q tests/test_v080_corner_phase73.py || goto :fail
"%PY%" -c "import qedcalc; print('QEDCalc', qedcalc.__version__); assert qedcalc.__version__=='0.80.0'" || goto :fail
echo v0.80 validation PASS
exit /b 0
:fail
echo v0.80 validation FAIL
exit /b 1
