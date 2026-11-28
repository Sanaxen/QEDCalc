@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_boundary_incremental_ibp %*
exit /b %errorlevel%
