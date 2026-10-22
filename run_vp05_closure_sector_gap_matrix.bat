@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_closure_sector_gap_matrix
exit /b %ERRORLEVEL%
