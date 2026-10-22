@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_sector202_two_column_modular_coefficients
exit /b %ERRORLEVEL%
