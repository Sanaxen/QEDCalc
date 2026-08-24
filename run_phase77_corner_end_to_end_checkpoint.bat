@echo off
setlocal
set "PY=.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"
"%PY%" -c "from qedcalc.operations.corner import corner_phase77_end_to_end_checkpoint as a; [print(k,':',v) for k,v in a().items()]"
"%PY%" -c "from qedcalc.operations.corner import corner_phase77_numerical_checkpoint as q; [print(r,q(r,power=10,seed=77,replicates=4)) for r in (0.02,0.01,0.005,0.002)]"
endlocal
