@echo off
call %~dp0\.venv\Scripts\activate.bat
python -m here %*
deactivate
