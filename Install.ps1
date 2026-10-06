$ErrorActionPreference = 'Stop'
$packageRoot = $PSScriptRoot
$installRoot = Join-Path $env:LOCALAPPDATA 'Programs\ModelLibraryOrganizer\1.0.30'
if (Test-Path -LiteralPath $installRoot) {
    throw "Installation already exists: $installRoot. Use the portable EXE, or choose a new installation directory."
}
New-Item -ItemType Directory -Path $installRoot | Out-Null
Get-ChildItem -LiteralPath $packageRoot | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $installRoot -Recurse
}
$shortcutPath = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Model Library Organizer 1.0.30.lnk'
$shellObject = New-Object -ComObject WScript.Shell
$shortcut = $shellObject.CreateShortcut($shortcutPath)
$shortcut.TargetPath = Join-Path $installRoot 'ModelLibraryOrganizer.exe'
$shortcut.WorkingDirectory = $installRoot
$shortcut.Save()
$installedFiles = @(Get-ChildItem -LiteralPath $installRoot -File -Recurse -Force | ForEach-Object { $_.FullName.Substring($installRoot.Length + 1) })
@{ application = 'ModelLibraryOrganizer'; installPath = $installRoot; files = $installedFiles } | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $installRoot '.installation.json') -Encoding UTF8
Write-Host "Installed: $installRoot"
Write-Host 'Models were not moved. User settings remain in LocalAppData\ModelLibraryOrganizer.'
Read-Host 'Press Enter to close'
