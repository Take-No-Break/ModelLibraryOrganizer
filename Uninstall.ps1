$ErrorActionPreference = 'Stop'
try {
    $installationPath = [IO.Path]::GetFullPath($PSScriptRoot).TrimEnd('\')
    $managedBase = [IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA 'Programs\ModelLibraryOrganizer')).TrimEnd('\')
    if ([IO.Path]::GetDirectoryName($installationPath) -ne $managedBase -or [IO.Path]::GetFileName($installationPath) -notmatch '^\d+\.\d+\.\d+$') {
        throw 'Only Install.cmd installations can be removed. Remove portable copies manually.'
    }
    if ((Get-Item -LiteralPath $installationPath).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Linked installation folder.' }
    $receiptPath = Join-Path $installationPath '.installation.json'
    $receipt = Get-Content -LiteralPath $receiptPath -Raw | ConvertFrom-Json
    if ($receipt.application -ne 'ModelLibraryOrganizer' -or $receipt.installPath -ne $installationPath) { throw 'Invalid installation receipt.' }
    if (Get-Process -Name ModelLibraryOrganizer -ErrorAction SilentlyContinue) { throw 'Close Model Library Organizer before uninstalling.' }
    $targets = @()
    foreach ($relativePath in $receipt.files) {
        if ([IO.Path]::IsPathRooted($relativePath)) { throw 'Invalid recorded path.' }
        $filePath = [IO.Path]::GetFullPath((Join-Path $installationPath $relativePath))
        if (-not $filePath.StartsWith($installationPath + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Path outside installation.' }
        $checkPath = $filePath
        while ($checkPath -ne $installationPath) {
            if (Test-Path -LiteralPath $checkPath) {
                if ((Get-Item -LiteralPath $checkPath -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Linked file or folder.' }
            }
            $checkPath = [IO.Path]::GetDirectoryName($checkPath)
        }
        if (Test-Path -LiteralPath $filePath -PathType Container) { throw 'Expected file, not directory.' }
        $targets += $filePath
    }
    Write-Host 'Remove this installation and its matching desktop shortcut?'
    Write-Host $installationPath
    Write-Host 'Models, captions, settings and restoration history will be kept.'
    if ((Read-Host 'Type YES to uninstall; anything else cancels') -cne 'YES') { exit 0 }
    $shortcutPath = Join-Path ([Environment]::GetFolderPath('Desktop')) ('Model Library Organizer ' + [IO.Path]::GetFileName($installationPath) + '.lnk')
    if (Test-Path -LiteralPath $shortcutPath) {
        $shellObject = New-Object -ComObject WScript.Shell
        if ($shellObject.CreateShortcut($shortcutPath).TargetPath -eq (Join-Path $installationPath 'ModelLibraryOrganizer.exe')) { Remove-Item -LiteralPath $shortcutPath }
    }
    foreach ($filePath in $targets) {
        if (Test-Path -LiteralPath $filePath -PathType Leaf) { Remove-Item -LiteralPath $filePath -Force }
    }
    Remove-Item -LiteralPath $receiptPath -Force
    $directories = @($targets | ForEach-Object {
        $directoryPath = [IO.Path]::GetDirectoryName($_)
        while ($directoryPath.StartsWith($installationPath + '\', [StringComparison]::OrdinalIgnoreCase)) {
            $directoryPath
            $directoryPath = [IO.Path]::GetDirectoryName($directoryPath)
        }
    }) | Sort-Object -Unique | Sort-Object Length -Descending
    foreach ($directoryPath in $directories) {
        if (Test-Path -LiteralPath $directoryPath -PathType Container) {
            if (@(Get-ChildItem -LiteralPath $directoryPath -Force).Count -eq 0) { Remove-Item -LiteralPath $directoryPath }
        }
    }
    if (@(Get-ChildItem -LiteralPath $installationPath -Force).Count -eq 0) { Remove-Item -LiteralPath $installationPath }
    Write-Host 'Uninstalled. Additional files and user data were preserved.'
} catch {
    Write-Host ('Uninstall stopped: ' + $_.Exception.Message)
    Read-Host 'Press Enter to close'
    exit 1
}
Read-Host 'Press Enter to close'
