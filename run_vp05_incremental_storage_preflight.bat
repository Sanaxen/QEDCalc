@echo off
setlocal
cd /d "%~dp0"
set "EQUATIONS=output\three_loop_integral_family_audit\vp05_target_symbolic_compressed.equations.json"
if not exist "%EQUATIONS%" (
 echo ERROR: Missing VP05 compressed equations: %EQUATIONS%
 exit /b 2
)
echo [VP05] Experimental incremental storage footprint only; no Fermat/Kira.
python -m examples.three_loop_sector203_incremental_storage_preflight --equations "%EQUATIONS%"
exit /b %ERRORLEVEL%
