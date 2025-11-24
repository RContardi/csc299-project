<#
Simple PowerShell launcher that forwards natural-language text to the
Python CLI's `say` command.

Usage:
  .\say.ps1 put buy a 2 liter container of milk on my tasks

This will run: python -m main say "put buy a 2 liter container of milk on my tasks"
#>
param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Text
)

if (-not $Text -or $Text.Count -eq 0) {
    Write-Host "Usage: .\say.ps1 <natural language text>"
    exit 1
}

$joined = $Text -join ' '
Write-Host "Sending to task manager: $joined"
python -m main say $joined
