@echo off
:: Check for administrative privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrative privileges.
) else (
    echo This script requires administrative privileges. Please run as administrator.
    pause
    exit /b
)

:: Reset TCP/IP stack
echo Resetting TCP/IP stack...
netsh int ip reset
if %errorLevel% neq 0 (
    echo Failed to reset TCP/IP stack. Some components might have failed.
)

:: Flush DNS cache
echo Flushing DNS cache...
ipconfig /flushdns
if %errorLevel% neq 0 (
    echo Failed to flush DNS cache.
    pause
    exit /b
)

:: Release and renew IP address
echo Releasing IP address...
ipconfig /release
if %errorLevel% neq 0 (
    echo Failed to release IP address.
)

echo Renewing IP address...
ipconfig /renew
if %errorLevel% neq 0 (
    echo Failed to renew IP address.
)

:: Restart network interface
echo Restarting network interface...
set interfaceName="Local Area Connection"  :: Change this to the actual name of your network interface
netsh interface set interface %interfaceName% admin=disable
if %errorLevel% neq 0 (
    echo Failed to disable network interface.
)
netsh interface set interface %interfaceName% admin=enable
if %errorLevel% neq 0 (
    echo Failed to enable network interface.
)

echo Checking if a restart is required...
netsh int ip reset | find "Restart the computer"
if %errorLevel% == 0 (
    echo A restart is required to complete the TCP/IP stack reset.
    echo Do you want to restart now? (Y/N)
    set /p restart_choice=
    if /i "%restart_choice%"=="Y" (
        echo Restarting the computer...
        shutdown /r /t 0
    ) else (
        echo Please restart the computer manually to complete the network reset.
    )
) else (
    echo Network reset complete without requiring a restart.
)

pause
