@echo off
echo ===============================
echo Building EXE
echo ===============================

echo Activating environment...
call venv\Scripts\activate.bat

echo Building EXE file...
pyinstaller --onefile ^
    --windowed ^
    --icon=assets/icon.ico ^
    --name=UserMonitor ^
    --add-data="config;config" ^
    --add-data="assets;assets" ^
    --hidden-import=win32clipboard ^
    --hidden-import=win32com ^
    --hidden-import=win32com.client ^
    --hidden-import=win32gui ^
    --hidden-import=win32process ^
    --hidden-import=pynput ^
    --hidden-import=pynput.keyboard ^
    --hidden-import=pynput.keyboard._win32 ^
    --hidden-import=pynput.mouse._win32 ^
    --hidden-import=psutil ^
    --hidden-import=logging ^
    --hidden-import=json ^
    --hidden-import=threading ^
    --hidden-import=time ^
    --hidden-import=os ^
    --hidden-import=sys ^
    --hidden-import=re ^
    --hidden-import=datetime ^
    run_all.py

echo Copying config and assets...
xcopy config dist\config /E /I /Y >nul
xcopy assets dist\assets /E /I /Y >nul

echo EXE ready: dist\UserMonitor.exe
deactivate
pause