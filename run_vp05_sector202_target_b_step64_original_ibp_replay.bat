@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_sector202_target_b_step64_original_ibp_replay %*
exit /b %ERRORLEVEL%
