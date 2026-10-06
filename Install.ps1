$ErrorActionPreference = 'Stop'
$packageRoot = $PSScriptRoot
$installRoot = Join-Path $env:LOCALAPPDATA 'Programs\ModelLibraryOrganizer\1.0.8'
if (Test-Path -LiteralPath $installRoot) {
    throw "Installation already exists: $installRoot. Use the portable EXE, or choose a new installation directory."
}
New-Item -ItemType Directory -Path $installRoot | Out-Null
Get-ChildItem -LiteralPath $packageRoot | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $installRoot -Recurse
}
$shortcutPath = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Model Library Organizer 1.0.8.lnk'
$shellObject = New-Object -ComObject WScript.Shell
$shortcut = $shellObject.CreateShortcut($shortcutPath)
$shortcut.TargetPath = Join-Path $installRoot 'ModelLibraryOrganizer.exe'
$shortcut.WorkingDirectory = $installRoot
$shortcut.Save()
Write-Host "Installed: $installRoot"
Write-Host 'Models were not moved. User settings remain in LocalAppData\ModelLibraryOrganizer.'
Read-Host 'Press Enter to close'
