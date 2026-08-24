@echo off
if exist .venv\Scripts\python.exe (
  .venv\Scripts\python.exe examples\phase49_corner_historical_K_projector_audit.py
) else (
  python examples\phase49_corner_historical_K_projector_audit.py
)
