@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_c_exact_rank_certificate
exit /b %errorlevel%
