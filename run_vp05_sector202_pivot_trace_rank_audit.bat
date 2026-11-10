@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_sector202_pivot_trace_rank_audit %*
exit /b %ERRORLEVEL%
