<#
Install script for Windows PowerShell to install the project in editable mode.
Usage: .\install.ps1
#>
Write-Host "Installing Task Manager in editable mode..."
python -m pip install --upgrade pip
python -m pip install -e .
Write-Host "Install complete. You can now run 'task-manager' from PowerShell."

# Attempt to create a Desktop shortcut using the helper script if it exists
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$createShortcut = Join-Path $scriptDir 'create_shortcut.ps1'
if (Test-Path $createShortcut) {
	Write-Host "Creating Desktop shortcut..."
	try {
		# If a custom icon exists in assets, pass it to the shortcut creator
		$iconCandidate = Join-Path $scriptDir 'assets\task_manager.ico'
		if (Test-Path $iconCandidate) {
			& $createShortcut -IconPath $iconCandidate
		} else {
			& $createShortcut
		}
		Write-Host "Shortcut creation attempted."
	} catch {
		Write-Warning "Shortcut creation failed: $_"
	}
} else {
	Write-Host "No create_shortcut.ps1 found; skipping shortcut creation."
}
