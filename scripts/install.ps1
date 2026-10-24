$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$target = Join-Path $env:LOCALAPPDATA 'LabLink'
$venv = Join-Path $target 'venv'
$python = Join-Path $venv 'Scripts\python.exe'
if (!(Test-Path $python)) {
    if (Get-Command py.exe -ErrorAction SilentlyContinue) {
        & py.exe -3 -m venv $venv
    } else {
        & python.exe -m venv $venv
    }
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.10+ is required. Install Python with tkinter first.' }
}
& $python -m pip install $root
if ($LASTEXITCODE -ne 0) { throw 'Package installation failed.' }
$desktop = [Environment]::GetFolderPath('Desktop')
$ws = New-Object -ComObject WScript.Shell
$link = $ws.CreateShortcut((Join-Path $desktop 'LabLink.lnk'))
$link.TargetPath = $python
$link.Arguments = '-m lablink gui'
$link.WorkingDirectory = $target
$link.Save()
Write-Host 'Installed independently. Existing remote-access tools were not changed.'
Write-Host "Configure: & `"$python`" -m lablink setup"
Write-Host 'Then double-click LabLink on the desktop.'
