@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_sector202_step51_exact_ibp_replay %*
exit /b %ERRORLEVEL%
