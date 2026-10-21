@echo off
setlocal
cd /d "%~dp0"
set "EQUATIONS=output\three_loop_integral_family_audit\vp05_target_symbolic_compressed.equations.json"
if not exist "%EQUATIONS%" (
 echo ERROR: Missing VP05 compressed witness: %EQUATIONS%
 exit /b 2
)
echo [VP05] Cell-accounting reconciliation ONLY. No Fermat/Kira.
python -m examples.three_loop_sector203_cell_accounting_reconciliation --equations "%EQUATIONS%"
exit /b %ERRORLEVEL%
