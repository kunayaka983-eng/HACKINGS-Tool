@echo off
setlocal EnableExtensions
chcp 65001 >nul
title OMEGA-7 - VirtualBox Kali Launcher
set "VM_NAME=Kali Linux"
set "SSH_USER=kali"
set "SSH_PORT=2222"
set "TOOLKIT_DIR=omega7"
set "VBOX=%ProgramFiles%\Oracle\VirtualBox\VBoxManage.exe"
if not exist "%VBOX%" (
  for %%G in (VBoxManage.exe) do set "VBOX=%%~$PATH:G"
)
if not exist "%VBOX%" (
  echo [ERROR] VirtualBox VBoxManage not found.
  pause
  exit /b 1
)
where ssh.exe >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Windows OpenSSH Client not found. Enable Optional Features - OpenSSH Client.
  pause
  exit /b 1
)
"%VBOX%" showvminfo "%VM_NAME%" --machinereadable >nul 2>&1
if errorlevel 1 (
  echo [ERROR] VM "%VM_NAME%" not found. Edit VM_NAME at the top of this BAT.
  "%VBOX%" list vms
  pause
  exit /b 1
)
"%VBOX%" showvminfo "%VM_NAME%" --machinereadable | findstr /C:"VMState=\"running\"" >nul
if errorlevel 1 (
  echo [INFO] Starting VirtualBox VM...
  "%VBOX%" startvm "%VM_NAME%" --type headless
  if errorlevel 1 (echo [ERROR] VM failed to start.& pause & exit /b 1)
)
echo [INFO] Connecting to Kali via SSH localhost:%SSH_PORT%.
echo [INFO] First boot can take a moment. Retry this BAT if SSH is not ready.
echo [INFO] Expected Kali path: ~/%TOOLKIT_DIR%/toolkit.py
echo.
ssh.exe -t -p %SSH_PORT% %SSH_USER%@127.0.0.1 "cd ~/%TOOLKIT_DIR% && python3 toolkit.py"
if errorlevel 1 echo [ERROR] SSH or toolkit launch failed. Read README.md setup steps.
pause
