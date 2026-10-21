@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_small_id_equation_role_audit
exit /b %ERRORLEVEL%
