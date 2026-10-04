# Bebe Names Studio PowerShell Launcher
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  🌸 Iniciando Bebe Names Studio..." -ForegroundColor Yellow
Write-Host "  Directorio: $scriptDir" -ForegroundColor Gray
Write-Host "========================================================" -ForegroundColor Cyan

# Open default browser after 1.5 seconds
Start-Job -ScriptBlock {
    Start-Sleep -Milliseconds 1500
    Start-Process "http://localhost:8000"
} | Out-Null

python server.py 8000
