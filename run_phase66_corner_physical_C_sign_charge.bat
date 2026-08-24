@echo off
setlocal
cd /d %~dp0
if exist ".venv\Scripts\python.exe" (set "PY=.venv\Scripts\python.exe") else (set "PY=python")
set "PYTHONPATH=%CD%"
"%PY%" -c "from qedcalc.operations.corner import corner_phase66_physical_C_sign_charge_audit as f; a=f(); print('Phase-66 corner physical C-sign charge audit'); [print(k,':',v) for k,v in a.items()]; print('Phase-66: PASS' if a['plus_candidate_residual']==0 and a['minus_candidate_residual']!=0 and a['resolved_physical_C_sign']==1 else 'Phase-66: FAIL')"
endlocal
