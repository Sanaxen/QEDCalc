@echo off
setlocal
set PY=.venv\Scripts\python.exe
if not exist "%PY%" set PY=python
set PYTHONPATH=%CD%
echo QEDCalc v0.82 validation
"%PY%" -c "from qedcalc.operations.corner import corner_phase73_finite_rho_cancellation_wick_audit as a, corner_phase75_retained_photon_residual_audit as b; x=a(); y=b(); assert x['D_cancel_euclidean_coefficient']==-1 and str(x['k2_cancel_euclidean_coefficient'])=='1/2' and str(x['k2_mass_residual_euclidean_coefficient'])=='-1/2' and y['scalar_residual_identity']==0 and y['uses_phase69_k2_quotient']; print('Phase-75 cancellation sign/residual audit PASS')" || goto :fail
"%PY%" -m pytest -q tests/test_corner.py -k phase75 || goto :fail
"%PY%" -c "import qedcalc; print('QEDCalc',qedcalc.__version__); assert qedcalc.__version__=='0.82.0'" || goto :fail
echo v0.82 validation PASS
exit /b 0
:fail
echo v0.82 validation FAIL
exit /b 1
