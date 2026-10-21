@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_exact_528_provenance_detail %*
exit /b %ERRORLEVEL%
