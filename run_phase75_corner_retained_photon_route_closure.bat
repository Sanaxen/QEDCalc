@echo off
setlocal
set PY=.venv\Scripts\python.exe
if not exist "%PY%" set PY=python
set PYTHONPATH=%CD%
"%PY%" -c "from qedcalc.operations.corner import corner_phase75_retained_photon_residual_audit as a; print(a())"
"%PY%" -c "from qedcalc.operations.corner import corner_phase75_route_closure_qmc as q; [print(r,q(r,power=9,seed=31,replicates=4)) for r in (0.05,0.02,0.01)]"
