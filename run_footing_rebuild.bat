@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "PARENT_DIR=%SCRIPT_DIR%.."
set "PYTHON=%PARENT_DIR%\.venv312\Scripts\python.exe"

if not exist "%PYTHON%" (
    echo Missing interpreter: "%PYTHON%"
    pause
    exit /b 1
)

pushd "%PARENT_DIR%"
"%PYTHON%" -m footing_rebuild.app
set "EXIT_CODE=%ERRORLEVEL%"
popd

if not "%EXIT_CODE%"=="0" (
    echo.
    echo footing_rebuild exited with an error.
    pause
)

endlocal & exit /b %EXIT_CODE%