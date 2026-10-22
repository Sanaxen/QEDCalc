@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_cross_basis_relation_audit
exit /b %ERRORLEVEL%
