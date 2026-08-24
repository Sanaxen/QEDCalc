@echo off
setlocal
set PY=.venv\Scripts\python.exe
if not exist "%PY%" set PY=python
set PYTHONPATH=%CD%
"%PY%" -c "from qedcalc.operations.corner import corner_phase76_soft_finite_ownership_audit as a; [print(k,':',v) for k,v in a().items()]"
"%PY%" -c "from qedcalc.operations.corner import corner_phase76_full_finite_qmc as q; [print(r,q(r,power=10,seed=41,replicates=4)) for r in (0.05,0.02,0.01,0.005,0.002)]"
