# 建立 Windows 免安裝版；在儲存庫目錄執行此腳本。
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    python -m venv .build-env
    if ($LASTEXITCODE -ne 0) { throw 'Failed to create build environment.' }
    $buildPython = Join-Path $PSScriptRoot '.build-env\Scripts\python.exe'
    & $buildPython -m pip install 'pyinstaller==6.22.3'
    if ($LASTEXITCODE -ne 0) { throw 'Failed to install PyInstaller.' }
    & $buildPython -m PyInstaller --noconfirm --clean --onefile --windowed --name CannonBattle --add-data 'assets/cannon_display.png;assets' GUI.py
    if ($LASTEXITCODE -ne 0) { throw 'Build failed.' }
    Compress-Archive -LiteralPath 'dist\CannonBattle.exe' -DestinationPath 'dist\CannonBattle-Windows-x64.zip' -Force
    Write-Output 'Ready: dist\CannonBattle-Windows-x64.zip'
}
finally {
    Pop-Location
}
