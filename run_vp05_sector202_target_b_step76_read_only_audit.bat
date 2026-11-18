@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_sector202_target_b_step76_read_only_audit %*
exit /b %ERRORLEVEL%
