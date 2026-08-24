@echo off
setlocal
cd /d %~dp0
if exist ".venv\Scripts\python.exe" (set "PY=.venv\Scripts\python.exe") else (set "PY=python")
set "PYTHONPATH=%CD%"
echo QEDCalc v0.79 validation
"%PY%" -c "from qedcalc.operations.corner import corner_phase72_full_stabilized_audit as f; a=f(); assert a['direct_log_scalar_split_residual']==0 and not a['direct_log_poles'] and a['checkpoint_is_input'] is False; print('Phase-72 ownership audit PASS')" || exit /b 1
"%PY%" -m pytest -q tests/test_corner.py::test_phase72_direct_log_unsplit_is_exact_and_checkpoint_not_input tests/test_corner.py::test_phase72_full_stabilized_qmc_smoke || exit /b 1
"%PY%" -c "import qedcalc; print('QEDCalc',qedcalc.__version__)" || exit /b 1
echo v0.79 validation PASS
endlocal
