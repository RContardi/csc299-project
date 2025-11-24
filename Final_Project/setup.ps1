# Stride Task Manager - Installation Script
# This script installs Stride and creates a desktop shortcut

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Stride Task Manager - Installation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$AppDir = $ScriptDir

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    Write-Host "  Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if required packages are installed
Write-Host ""
Write-Host "Installing required Python packages..." -ForegroundColor Yellow

$RequiredPackages = @("openai", "pillow")
foreach ($package in $RequiredPackages) {
    Write-Host "  Installing $package..." -ForegroundColor Gray
    python -m pip install $package --quiet --disable-pip-version-check
}
Write-Host "[OK] All packages installed" -ForegroundColor Green

# Check for OpenAI API key
Write-Host ""
Write-Host "Checking OpenAI API Key..." -ForegroundColor Yellow
$apiKey = [System.Environment]::GetEnvironmentVariable("OPENAI_API_KEY", "User")

if (-not $apiKey) {
    Write-Host "[WARNING] OPENAI_API_KEY not found in environment variables" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please enter your OpenAI API Key:" -ForegroundColor Yellow
    Write-Host "(Get one from: https://platform.openai.com/api-keys)" -ForegroundColor Gray
    $apiKey = Read-Host "API Key"
    
    if ($apiKey) {
        [System.Environment]::SetEnvironmentVariable("OPENAI_API_KEY", $apiKey, "User")
        Write-Host "[OK] API Key saved to environment variables" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] No API Key provided. You will need to set OPENAI_API_KEY manually." -ForegroundColor Yellow
    }
} else {
    Write-Host "[OK] API Key found" -ForegroundColor Green
}

# Create desktop shortcut
Write-Host ""
Write-Host "Creating desktop shortcut..." -ForegroundColor Yellow

$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "Stride.lnk"
$IcoPath = Join-Path $AppDir "desktop_icon.ico"
$MainPath = Join-Path $AppDir "main.py"

# Create shortcut using PowerShell
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "pythonw.exe"
$Shortcut.Arguments = "`"$MainPath`""
$Shortcut.WorkingDirectory = $AppDir
$Shortcut.Description = "Stride - AI Task Manager"
$Shortcut.IconLocation = $IcoPath
$Shortcut.Save()

Write-Host "[OK] Desktop shortcut created: $ShortcutPath" -ForegroundColor Green

# Create a Start Menu shortcut as well
Write-Host ""
Write-Host "Creating Start Menu shortcut..." -ForegroundColor Yellow

$StartMenuPath = [Environment]::GetFolderPath("StartMenu")
$ProgramsPath = Join-Path $StartMenuPath "Programs"
$StartShortcutPath = Join-Path $ProgramsPath "Stride.lnk"

$StartShortcut = $WScriptShell.CreateShortcut($StartShortcutPath)
$StartShortcut.TargetPath = "pythonw.exe"
$StartShortcut.Arguments = "`"$MainPath`""
$StartShortcut.WorkingDirectory = $AppDir
$StartShortcut.Description = "Stride - AI Task Manager"
$StartShortcut.IconLocation = $IcoPath
$StartShortcut.Save()

Write-Host "[OK] Start Menu shortcut created" -ForegroundColor Green

# Installation complete
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Stride has been installed successfully!" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now:" -ForegroundColor White
Write-Host "  - Launch Stride from your Desktop" -ForegroundColor Gray
Write-Host "  - Find it in your Start Menu" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Enter to exit..." -ForegroundColor Yellow
Read-Host
