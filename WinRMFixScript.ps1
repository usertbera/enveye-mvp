# WinRM Fixer Script
Write-Host "🔧 Configuring WinRM..." -ForegroundColor Cyan

# Enable WinRM Service
winrm quickconfig -q

# Allow Unencrypted Traffic
winrm set winrm/config/service '@{AllowUnencrypted="true"}'

# Allow Basic Authentication
winrm set winrm/config/service/auth '@{Basic="true"}'

# Create Firewall Rule to Allow Port 5985
New-NetFirewallRule -DisplayName "Allow WinRM (HTTP 5985)" -Name "AllowWinRM" -Protocol TCP -LocalPort 5985 -Action Allow

# Verify Listener
Write-Host "`n🔎 Current Listeners:" -ForegroundColor Green
winrm enumerate winrm/config/listener

Write-Host "`n✅ WinRM Setup Completed Successfully!" -ForegroundColor Green
