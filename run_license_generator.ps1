$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$parentDir = Split-Path -Parent $scriptDir
$python = Join-Path $parentDir ".venv312\Scripts\python.exe"

if (-not (Test-Path $python)) {
    Write-Error "Missing interpreter: $python"
    exit 1
}

Push-Location $parentDir
try {
    & $python -m footing_rebuild.tools.license_generator_ui
    $exitCode = $LASTEXITCODE
}
finally {
    Pop-Location
}

if ($exitCode -ne 0) {
    Write-Host ""
    Write-Host "license_generator_ui exited with an error."
}

exit $exitCode