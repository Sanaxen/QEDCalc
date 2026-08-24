@echo off
setlocal
set PY=.venv\Scripts\python.exe
if not exist "%PY%" set PY=python
set PYTHONPATH=%CD%
echo QEDCalc v0.83 validation
"%PY%" -c "from qedcalc.operations.corner import corner_phase76_soft_finite_ownership_audit as a; x=a(); assert x['ownership_residual']==0 and x['independent_checkpoint_residual']==0 and not x['checkpoint_used_as_input']; print('Phase-76 soft finite ownership audit PASS')" || goto :fail
"%PY%" -m pytest -q tests/test_v083_corner_phase76.py -k "phase76_soft_finite_ownership_is_exact" || goto :fail
"%PY%" -c "import qedcalc; print('QEDCalc',qedcalc.__version__); assert qedcalc.__version__=='0.83.0'" || goto :fail
echo v0.83 validation PASS
exit /b 0
:fail
echo v0.83 validation FAIL
exit /b 1
