@echo off
setlocal

echo 🚀 Starting Python venv setup...

REM Create venv if not exists
if not exist "venv\Scripts\activate.bat" (
    echo 🔧 Creating virtual environment...
    python -m venv venv
)

REM Detect shell environment
set "SHELL_TYPE=%ComSpec%"
echo 🔍 Shell detected: %SHELL_TYPE%

REM Activate venv depending on shell
if exist "%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" (
    echo ⚙️  You're likely in PowerShell — activate manually:
    echo 📌 Run: .\venv\Scripts\Activate.ps1
) else (
    echo ⚙️  Activating in CMD...
    call venv\Scripts\activate.bat
)

echo 🧪 Installing dependencies...
pip install --upgrade pip
pip install jinja2 python-terraform boto3

echo 💾 Freezing requirements...
pip freeze > requirements.txt

echo ✅ Setup complete.
pause