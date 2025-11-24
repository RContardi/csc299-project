<#
Create a Desktop shortcut to launch the Task Manager quick-add GUI.

This script creates a shortcut named "Task Manager - Quick Add.lnk" on the
current user's Desktop. It will attempt to use `pythonw` (no console) and
fall back to `python` if `pythonw` is not available.

Usage (PowerShell, from project root):
  .\create_shortcut.ps1

The script locates `say_app.py` relative to its own location, so place it in
the project root or run the script from the project root.
#>
param(
    [string]$IconPath
)

try {
    $scriptPath = $MyInvocation.MyCommand.Definition
    $projectRoot = Split-Path -Parent $scriptPath

    $appPath = Join-Path $projectRoot 'say_app.py'
    if (-not (Test-Path $appPath)) {
        Write-Error "say_app.py not found at $appPath. Run this script from the project root or move it into the project root."
        exit 1
    }

    # Prefer pythonw (no console). If not found, fallback to python.
    $pyCmd = (Get-Command pythonw -ErrorAction SilentlyContinue)
    if ($pyCmd) {
        $pythonExe = $pyCmd.Source
    } else {
        $pyCmd = (Get-Command python -ErrorAction SilentlyContinue)
        if ($pyCmd) { $pythonExe = $pyCmd.Source } else { $pythonExe = 'python' }
    }

    $desktop = [Environment]::GetFolderPath('Desktop')
    $lnkPath = Join-Path $desktop 'Task Manager - Quick Add.lnk'

    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($lnkPath)
    $shortcut.TargetPath = $pythonExe
    # Quote the app path to be safe with spaces
    $shortcut.Arguments = "`"$appPath`""
    $shortcut.WorkingDirectory = $projectRoot
    # Use custom icon if provided, otherwise default to python exe
    if ($IconPath) {
        if (-not (Test-Path $IconPath)) {
            Write-Warning "Icon path '$IconPath' not found; falling back to python executable icon."
            $shortcut.IconLocation = "$pythonExe,0"
        } else {
            $shortcut.IconLocation = $IconPath
        }
    } else {
        $shortcut.IconLocation = "$pythonExe,0"
    }
    $shortcut.Save()

    Write-Host "Created shortcut: $lnkPath (target: $pythonExe $appPath)"
} catch {
    Write-Error "Failed to create shortcut: $_"
    exit 1
}
