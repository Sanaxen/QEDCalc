@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_sector202_exact_source_export
exit /b %ERRORLEVEL%
