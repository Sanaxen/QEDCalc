@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_c_saved_rank_audit
exit /b %errorlevel%
