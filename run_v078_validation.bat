@echo off
setlocal
cd /d %~dp0
if exist ".venv\Scripts\python.exe" (set "PY=.venv\Scripts\python.exe") else (set "PY=python")
set "PYTHONPATH=%CD%"
echo QEDCalc v0.78 validation
"%PY%" -c "from qedcalc.operations.corner import corner_phase71_cancellation_first_overlap_measure_audit as f; a=f(); assert all(a[k]==0 for k in ('triangle_ad_jacobian_residual','triangle_upper_boundary_residual','line_ad_jacobian_residual','line_upper_boundary_residual')); print('Phase-71 exact measure audit PASS')" || exit /b 1
"%PY%" -m pytest -q tests/test_corner.py::test_phase71_cancellation_first_overlap_measure_is_exact tests/test_corner.py::test_phase71_overlap_qmc_smoke || exit /b 1
"%PY%" -c "import qedcalc; print('QEDCalc',qedcalc.__version__)" || exit /b 1
echo v0.78 validation PASS
endlocal
