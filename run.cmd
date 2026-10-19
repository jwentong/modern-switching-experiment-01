@echo off
setlocal
set "MPLCONFIGDIR=%~dp0..\.mplconfig"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
"%~dp0..\Python312\python.exe" %*
