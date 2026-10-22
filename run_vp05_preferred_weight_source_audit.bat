@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_preferred_weight_source_audit
exit /b %ERRORLEVEL%
