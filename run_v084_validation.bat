@echo off
setlocal
set "PY=.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"
echo QEDCalc v0.84 validation
"%PY%" -c "from qedcalc.operations.corner import corner_phase77_end_to_end_checkpoint as a; x=a(); assert x['sector_route_residual']==0 and x['matching_route_residual']==0 and x['route_to_route_residual']==0 and x['closed_form_residual']==0 and x['combined_ir_log_coefficient']==0 and x['combined_finite_checkpoint_residual']==0; print('Phase-77 end-to-end corner closure PASS')" || goto :fail
"%PY%" -m pytest -q tests/test_v084_corner_phase77.py -k "end_to_end_corner_closure_is_exact" || goto :fail
"%PY%" -c "import qedcalc; print('QEDCalc',qedcalc.__version__); assert qedcalc.__version__=='0.84.0'" || goto :fail
echo v0.84 validation PASS
exit /b 0
:fail
echo v0.84 validation FAIL
exit /b 1
