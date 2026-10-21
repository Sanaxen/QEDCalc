@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_kiradb_equation_sample
exit /b %ERRORLEVEL%
