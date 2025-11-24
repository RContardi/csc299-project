<#
Prompt for an .ico file, copy it into ./assets/task_manager.ico, and recreate
the Desktop shortcut using the project's helper.

Usage:
  powershell -ExecutionPolicy Bypass -File .\scripts\import_icon.ps1
#>
try {
    $src = Read-Host "Enter the path to your .ico file (drag-and-drop supported)"
    if (-not $src) {
        Write-Error "No path provided. Aborting."
        exit 1
    }

    $src = $src.Trim('"')
    if (-not (Test-Path $src)) {
        Write-Error "File not found: $src"
        exit 1
    }

    $projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Definition)
    $assetsDir = Join-Path $projectRoot 'assets'
    if (-not (Test-Path $assetsDir)) {
        New-Item -ItemType Directory -Path $assetsDir | Out-Null
    }

    $dst = Join-Path $assetsDir 'task_manager.ico'
    Copy-Item -Path $src -Destination $dst -Force
    Write-Host "Copied icon to: $dst"

    # Recreate the shortcut using project helper
    $createShortcut = Join-Path $projectRoot 'create_shortcut.ps1'
    if (Test-Path $createShortcut) {
        Write-Host "Recreating desktop shortcut with new icon..."
        & $createShortcut -IconPath $dst
        Write-Host "Done."
    } else {
        Write-Warning "create_shortcut.ps1 not found. Icon copied but shortcut not recreated."
    }
} catch {
    Write-Error "Error importing icon: $_"
    exit 1
}
