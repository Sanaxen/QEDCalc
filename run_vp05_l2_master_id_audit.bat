@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_l2_master_id_audit
exit /b %ERRORLEVEL%
