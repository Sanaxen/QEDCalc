@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_sector202_target_b_step53_exact_candidate %*
exit /b %ERRORLEVEL%
