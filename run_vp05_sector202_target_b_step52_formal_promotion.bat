@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_sector202_target_b_step52_formal_promotion %*
exit /b %ERRORLEVEL%
