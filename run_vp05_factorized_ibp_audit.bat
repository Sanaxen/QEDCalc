@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_factorized_ibp_audit %*
exit /b %errorlevel%
