@echo off
echo Setting up Grand Stay Hotel Management System...
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

:: Create virtual environment
echo Creating virtual environment...
python -m venv grandstay_env

:: Check if venv was created
if not exist "grandstay_env\Scripts\activate.bat" (
    echo ERROR: Virtual environment creation failed
    echo Please check Python installation
    pause
    exit /b 1
)

:: Activate virtual environment
echo Activating virtual environment...
call grandstay_env\Scripts\activate.bat

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install required packages
echo Installing packages...
pip install streamlit supabase pandas plotly python-dotenv

:: Create requirements file
echo Creating requirements.txt...
pip freeze > requirements.txt

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo To activate the virtual environment, run:
echo grandstay_env\Scripts\activate.bat
echo.
echo Then run your app with:
echo streamlit run app.py
echo.
pause