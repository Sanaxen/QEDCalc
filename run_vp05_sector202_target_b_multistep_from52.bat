@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_sector202_target_b_multistep_from52 %*
exit /b %ERRORLEVEL%
