@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
set "PY=.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"
if not exist test_results mkdir test_results
for /f %%A in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set STAMP=%%A
set "OUT=test_results\v055_%STAMP%"
mkdir "%OUT%"
call :run phase30 examples\phase30_self_energy_renormalized_outer_bridge.py || goto :done
call :run phase31 examples\phase31_self_energy_raw_to_final.py || goto :done
call :run phase32 examples\phase32_corner_raw_pair_bridge.py || goto :done
call :run phase33 examples\phase33_corner_parametric_family.py || goto :done
call :run phase34 examples\phase34_corner_raw_projector.py || goto :done
"%PY%" -m pytest -q tests\test_self_energy.py tests\test_corner.py > "%OUT%\focused_tests.log" 2>&1
set RC=%ERRORLEVEL%
:done
if not defined RC set RC=%ERRORLEVEL%
> "%OUT%\exit_code.txt" echo %RC%
powershell -NoProfile -Command "Compress-Archive -Path '%OUT%\*' -DestinationPath 'test_results\v055_%STAMP%.zip' -Force" >nul 2>&1
echo Validation complete. Exit code: %RC%
exit /b %RC%
:run
set NAME=%~1
set SCRIPT=%~2
"%PY%" "%SCRIPT%" > "%OUT%\%NAME%.log" 2>&1
if errorlevel 1 (set RC=%ERRORLEVEL% & exit /b %RC%)
exit /b 0
