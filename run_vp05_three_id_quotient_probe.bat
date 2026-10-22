@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_three_id_quotient_probe
exit /b %ERRORLEVEL%
