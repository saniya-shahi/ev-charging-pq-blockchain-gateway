param(
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

Write-Host "[SERVER] Starting backend at http://0.0.0.0:$Port"
Write-Host "[SERVER] Use this machine's LAN IP for clients."
uvicorn backend.main:app --host 0.0.0.0 --port $Port --workers 1
