param(
    [string]$ServerIp = "172.16.46.192",
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$pythonExe = Join-Path $projectRoot "evcrypto_env\Scripts\python.exe"
$activateScript = Join-Path $projectRoot "evcrypto_env\Scripts\Activate.ps1"

if (-not (Test-Path $pythonExe)) {
    Write-Host "[SETUP] Creating virtual environment..."
    python -m venv evcrypto_env
}

if (-not (Test-Path $activateScript)) {
    throw "Virtual environment activation script not found."
}

. $activateScript
Write-Host "[SETUP] Installing/updating dependencies..."
pip install -r requirements.txt | Out-Null

$env:GRID_URL = "http://$ServerIp`:$Port"
Write-Host "[CLIENT] GRID_URL set to $env:GRID_URL"
Write-Host "[CLIENT] Starting main_flow.py..."
python main_flow.py
