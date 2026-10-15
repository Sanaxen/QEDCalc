@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)
".venv\Scripts\python.exe" -m examples.three_loop_master_basis_candidate_sector_refine %*
exit /b %ERRORLEVEL%
