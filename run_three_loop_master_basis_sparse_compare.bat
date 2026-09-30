@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if "%~1"=="" goto :usage
if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  exit /b 1
)
".venv\Scripts\python.exe" -m examples.three_loop_master_basis_sparse_compare --family "%~1" --levels %~2 %~3
set "ERR=%ERRORLEVEL%"
endlocal
exit /b %ERR%
:usage
echo Usage: %~nx0 FAMILY LEVEL1 LEVEL2
echo Example: %~nx0 Q03_full 0 1
exit /b 2
