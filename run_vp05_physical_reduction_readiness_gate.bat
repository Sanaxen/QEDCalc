@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_physical_reduction_readiness_gate %*
exit /b %ERRORLEVEL%
