$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host '=== 1. Python virtual environment ===' -ForegroundColor Cyan
if (-not (Test-Path 'venv\Scripts\python.exe')) {
    python -m venv venv
}
& '.\venv\Scripts\python.exe' -m pip install --upgrade pip
& '.\venv\Scripts\python.exe' -m pip install -r requirements.txt

Write-Host '=== 2. Database (SQLite) ===' -ForegroundColor Cyan
& '.\venv\Scripts\python.exe' manage.py migrate

Write-Host '=== 3. Generate the mock dataset ===' -ForegroundColor Cyan
& '.\venv\Scripts\python.exe' manage.py generate_mock_data

Write-Host '=== 4. Train and evaluate the AI model ===' -ForegroundColor Cyan
& '.\venv\Scripts\python.exe' manage.py train_model

Write-Host '=== 5. Load mock data and demo account ===' -ForegroundColor Cyan
& '.\venv\Scripts\python.exe' manage.py seed_data

Write-Host '=== 6. React dependencies ===' -ForegroundColor Cyan
if (-not (Test-Path 'frontend\node_modules')) {
    Push-Location frontend
    npm install
    Pop-Location
}

Write-Host ''
Write-Host 'Setup complete.' -ForegroundColor Green
Write-Host 'Start the app with: .\run_local.ps1'
Write-Host 'Login with: demo / demo12345'
