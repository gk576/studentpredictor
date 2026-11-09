$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $root 'venv\Scripts\python.exe'
$frontend = Join-Path $root 'frontend'

if (-not (Test-Path $python)) {
    Write-Host 'Virtual environment not found. Run .\setup_local.ps1 first.' -ForegroundColor Red
    exit 1
}

Start-Process powershell -ArgumentList @(
    '-NoExit',
    '-Command',
    "Set-Location '$root'; & '$python' manage.py runserver 127.0.0.1:8000"
)

Start-Process powershell -ArgumentList @(
    '-NoExit',
    '-Command',
    "Set-Location '$frontend'; npm start"
)

Write-Host ''
Write-Host 'EduPredict is starting locally:' -ForegroundColor Green
Write-Host '  Frontend: http://localhost:3000'
Write-Host '  API:      http://127.0.0.1:8000/api/'
Write-Host '  Admin:    http://127.0.0.1:8000/admin/'
Write-Host '  Login:    demo / demo12345'
