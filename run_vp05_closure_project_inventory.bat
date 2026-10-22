@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_closure_project_inventory
exit /b %ERRORLEVEL%
