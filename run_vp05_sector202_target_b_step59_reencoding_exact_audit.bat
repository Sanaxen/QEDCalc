@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_sector202_target_b_step59_reencoding_exact_audit %*
exit /b %ERRORLEVEL%
