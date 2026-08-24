@echo off
setlocal
cd /d %~dp0
if exist ".venv\Scripts\python.exe" (set "PY=.venv\Scripts\python.exe") else (set "PY=python")
set "PYTHONPATH=%CD%"
"%PY%" -c "from qedcalc.operations.corner import corner_phase67_secondary_overlap_measure_audit as a, corner_rational_joint_secondary_qmc as q; print('Phase-67 audit',a()); print(q(0.05,power=10,seed=7))"
endlocal
