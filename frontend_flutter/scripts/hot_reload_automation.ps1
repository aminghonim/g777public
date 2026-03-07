function Send-FlutterReload {
    param([string]$key = "r")
    Write-Host "🚀 Sending '$key' to Flutter process..." -ForegroundColor Cyan
    # This is a placeholder for actual process injection or named pipe communication
    # In a real scenario, we would use external tools to send keys to the running terminal
}

# Monitoring loop for file changes
Get-ChildItem -Path "./lib" -Recurse | Watch-Path {
    Send-FlutterReload
}
