@echo off
rem ============================================
rem  PDF2zh MegaPower定制版 - hidden launcher
rem  - Server already running -> just open the Web UI
rem  - Not running -> start a hidden watchdog that runs the server
rem    (the watchdog also respawns the server after a Web UI restart)
rem  Stop the server from the Web UI ("停止服务" button).
rem ============================================

cd /d "%~dp0"

curl -s -m 2 -o nul "http://127.0.0.1:8890/health" 2>nul
if not errorlevel 1 (
    start "" "http://127.0.0.1:8890/"
    exit /b 0
)

rem First run: install base dependencies (flask/toml/pypdf/PyMuPDF/packaging)
py -3 -c "import flask, toml, pypdf, fitz, packaging" 2>nul
if errorlevel 1 (
    echo [SETUP] Installing base dependencies, please wait...
    py -3 -m pip install -r "%~dp0PDF2zh-MegaPower\server\requirements.txt" -i https://mirrors.ustc.edu.cn/pypi/simple
)

start "" "%~dp0PDF2zh-MegaPower\launcher.html"
powershell -NoProfile -WindowStyle Hidden -Command "$flag='%~dp0PDF2zh-MegaPower\server\_restart.flag'; while($true){ if(Test-Path $flag){Remove-Item $flag -Force -ErrorAction SilentlyContinue}; $p=Start-Process -WindowStyle Hidden -PassThru -FilePath 'py.exe' -ArgumentList '-3','server.py' -WorkingDirectory '%~dp0PDF2zh-MegaPower\server' -RedirectStandardOutput '%~dp0PDF2zh-MegaPower\server\server_console.log' -RedirectStandardError '%~dp0PDF2zh-MegaPower\server\server_console_err.log'; $p.WaitForExit(); if(Test-Path $flag){Remove-Item $flag -Force -ErrorAction SilentlyContinue} else {break} }"
exit /b 0
