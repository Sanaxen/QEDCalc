@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_sector202_pivot_mismatch_exact_spot %*
exit /b %ERRORLEVEL%
