@echo off
setlocal
set "VM_NAME=Kali Linux"
set "VBOX=%ProgramFiles%\Oracle\VirtualBox\VBoxManage.exe"
if not exist "%VBOX%" (echo VBoxManage.exe not found.& pause & exit /b 1)
echo VM must be fully powered OFF, not saved or running.
echo This adds TCP localhost:2222 to guest port 22 on NAT Adapter 1.
choice /M "Continue"
if errorlevel 2 exit /b 0
"%VBOX%" modifyvm "%VM_NAME%" --natpf1 "omega7ssh,tcp,127.0.0.1,2222,,22"
if errorlevel 1 (echo Could not add rule. Check VM name, adapter mode, VM state, or duplicate rule.) else (echo Forwarding rule added.)
pause
