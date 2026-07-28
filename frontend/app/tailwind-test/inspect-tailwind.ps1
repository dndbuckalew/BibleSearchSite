# ==========================================
# Tailwind Diagnostic
# ==========================================

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Frontend = Resolve-Path (Join-Path $ScriptDir "..\..")

Set-Location $Frontend

Write-Host ""
Write-Host "Frontend Root:"
Write-Host (Get-Location)

Write-Host ""
Write-Host "Files:"
Get-ChildItem
