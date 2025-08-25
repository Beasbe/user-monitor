@echo off
echo ===============================
echo UserMonitor Setup
echo ===============================

echo Step 1: Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Failed to create virtual environment
    pause
    exit /b 1
)

echo Step 2: Activating environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate environment
    pause
    exit /b 1
)

echo Step 3: Installing dependencies from requirements.txt...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

echo Step 4: Installing PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo Failed to install PyInstaller
    pause
    exit /b 1
)

echo Step 5: Verifying installations...
python -c "import pynput; print('pynput: OK')"
python -c "import win32com; print('pywin32: OK')"
python -c "import psutil; print('psutil: OK')"
python -c "import PyInstaller; print('PyInstaller: OK')"

echo.
echo ===============================
echo Setup completed successfully!
echo ===============================
echo.
echo Now you can run:
echo   build.bat    - to compile EXE
echo   run.bat      - to run Python script
pause