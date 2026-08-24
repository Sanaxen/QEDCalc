@echo off
setlocal
set PY=.venv\Scripts\python.exe
if not exist "%PY%" set PY=python
set PYTHONPATH=%CD%
echo QEDCalc v0.81 validation
"%PY%" -c "from qedcalc.operations.corner import corner_phase74_k2_mass_residual_nonuniform_audit as a; x=a(); assert x['fixed_k_rho0_limit']==0 and x['soft_scaled_rho0_limit']!=0 and x['can_discard_before_integration'] is False; print('Phase-74 non-uniform residual audit PASS')" || goto :fail
"%PY%" -m pytest -q tests/test_corner.py -k phase74 || goto :fail
"%PY%" -c "import qedcalc; print('QEDCalc',qedcalc.__version__); assert qedcalc.__version__=='0.81.0'" || goto :fail
echo v0.81 validation PASS
exit /b 0
:fail
echo v0.81 validation FAIL
exit /b 1
