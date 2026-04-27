# Create a dedicated venv for MCP to avoid conflicts with main project
$venvPath = Join-Path $PSScriptRoot ".venv"
Write-Host "Creating isolated virtual environment at $venvPath..."
python -m venv $venvPath

# Path to the new pip
$pipPath = Join-Path $venvPath "Scripts\pip.exe"

# Install requirements
Write-Host "Installing dependencies in isolated environment..."
& $pipPath install -r (Join-Path $PSScriptRoot "requirements.txt")

# Dependencies needed for imported backend modules (cloud_service.py)
& $pipPath install requests python-dotenv

Write-Host "✅ MCP Environment Setup Complete!"
Write-Host "Python Path: $(Join-Path $venvPath 'Scripts\python.exe')"
