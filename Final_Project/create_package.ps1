# Create distributable package for Stride
Write-Host "Creating Stride distribution package..." -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$DistDir = Join-Path $ScriptDir "Stride-Installer"
$ZipFile = Join-Path $ScriptDir "Stride-Installer.zip"

# Remove old distribution if it exists
if (Test-Path $DistDir) {
    Remove-Item -Path $DistDir -Recurse -Force
}
if (Test-Path $ZipFile) {
    Remove-Item -Path $ZipFile -Force
}

# Create distribution directory
New-Item -Path $DistDir -ItemType Directory | Out-Null

# Copy necessary files
Write-Host "Copying files..." -ForegroundColor Yellow

$FilesToCopy = @(
    "main.py",
    "gui.py",
    "setup.ps1",
    "INSTALL.bat",
    "INSTALLATION_GUIDE.md",
    "DISTRIBUTION_README.md",
    "desktop_icon.ico",
    "stride_logo.png",
    "tasks_icon.png",
    "task_manager"
)

foreach ($file in $FilesToCopy) {
    $sourcePath = Join-Path $ScriptDir $file
    $destPath = Join-Path $DistDir $file
    
    if (Test-Path $sourcePath) {
        if (Test-Path $sourcePath -PathType Container) {
            Copy-Item -Path $sourcePath -Destination $destPath -Recurse -Force
            Write-Host "  Copied folder: $file" -ForegroundColor Gray
        } else {
            Copy-Item -Path $sourcePath -Destination $destPath -Force
            Write-Host "  Copied: $file" -ForegroundColor Gray
        }
    } else {
        Write-Host "  Not found: $file" -ForegroundColor Yellow
    }
}

# Create requirements.txt
$reqPath = Join-Path $DistDir "requirements.txt"
if (-not (Test-Path $reqPath)) {
    Set-Content -Path $reqPath -Value "openai>=1.0.0" -Encoding UTF8
    Add-Content -Path $reqPath -Value "pillow>=10.0.0" -Encoding UTF8
    Write-Host "  Created requirements.txt" -ForegroundColor Gray
}

# Clean up cache directories
Get-ChildItem -Path $DistDir -Recurse -Directory -Filter "__pycache__" | ForEach-Object {
    Remove-Item -Path $_.FullName -Recurse -Force
}
Write-Host "  Cleaned cache files" -ForegroundColor Gray

# Remove database file
$dbPath = Join-Path $DistDir "tasks.db"
if (Test-Path $dbPath) {
    Remove-Item -Path $dbPath -Force
    Write-Host "  Removed database file" -ForegroundColor Gray
}

# Create a parent folder to keep everything organized
$ParentDir = Join-Path $ScriptDir "Stride"
if (Test-Path $ParentDir) {
    Remove-Item -Path $ParentDir -Recurse -Force
}
New-Item -Path $ParentDir -ItemType Directory | Out-Null

# Move the Stride-Installer contents into the Stride folder
Move-Item -Path "$DistDir\*" -Destination $ParentDir -Force
Remove-Item -Path $DistDir -Force

# Create ZIP file with the Stride folder
Write-Host ""
Write-Host "Creating ZIP archive..." -ForegroundColor Yellow
Compress-Archive -Path $ParentDir -DestinationPath $ZipFile -Force
Write-Host "Created: Stride-Installer.zip" -ForegroundColor Green

# Clean up temp directory
Remove-Item -Path $ParentDir -Recurse -Force

# Show final message
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Package Created Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Distribution file: $ZipFile" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now share this ZIP file." -ForegroundColor White
Write-Host "Users should:" -ForegroundColor White
Write-Host "  1. Extract the ZIP" -ForegroundColor Gray
Write-Host "  2. Run INSTALL.bat" -ForegroundColor Gray
Write-Host "  3. Follow the setup prompts" -ForegroundColor Gray
Write-Host ""
