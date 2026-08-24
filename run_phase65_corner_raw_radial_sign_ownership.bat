@echo off
setlocal
cd /d %~dp0
if exist ".venv\Scripts\python.exe" (
  set "PY=.venv\Scripts\python.exe"
) else (
  set "PY=python"
)
set "PYTHONPATH=%CD%"
"%PY%" -c "from qedcalc.operations.corner import corner_phase65_raw_radial_sign_ownership_audit as f; print('Phase-65 corner raw-radial sign ownership'); [print(k,':',v) for k,v in f().items()]; print('Phase-65: PASS' if f()['scalar_n3_residual']==0 and f()['raw_C_sign']==-1 and f()['physical_bridge_C_sign']==1 else 'Phase-65: FAIL')"
endlocal
