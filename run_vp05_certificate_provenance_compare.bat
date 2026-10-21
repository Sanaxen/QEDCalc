@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_certificate_provenance_compare %*
exit /b %ERRORLEVEL%
