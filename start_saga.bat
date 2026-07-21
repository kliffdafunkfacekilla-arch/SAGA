@echo off
echo Starting S.A.G.A. Engine Boot Sequence...
echo =========================================
echo.

echo [1] Verifying model presence...
set "MODEL_DIR=%~dp0models"
if not exist "%MODEL_DIR%" (
    powershell -command "Add-Type -AssemblyName PresentationFramework;[System.Windows.MessageBox]::Show('Models directory not found. Please create a folder named \"models\" and place a .gguf file there.','Missing Models','OK','Error')"
    echo [ERROR] Models directory not found: %MODEL_DIR%
    pause
    exit /b 1
)
rem Look for any .gguf file – the first one will be used by AIDirector
for %%F in ("%MODEL_DIR%\*.gguf") do (
    set "MODEL_FILE=%%~fF"
    goto :found_model
)
:found_model
if "%MODEL_FILE%"=="" (
    powershell -command "Add-Type -AssemblyName PresentationFramework;[System.Windows.MessageBox]::Show('No .gguf model file found in models folder. Please place a GGUF model file.','Missing Model','OK','Error')"
    echo [ERROR] No .gguf model file found in %MODEL_DIR%
    pause
    exit /b 1
)
echo.

echo [2] Launching S.A.G.A. B.R.U.T.A.L. Engine...
echo =========================================
python -m pip install -r requirements.txt --quiet
python main_controller.py

if %errorlevel% neq 0 (
    echo.
    echo [CRITICAL ERROR] The Engine crashed. See output above.
    pause
)
