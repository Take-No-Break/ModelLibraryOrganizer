# Release preparation

Repository: https://github.com/Take-No-Break/ModelLibraryOrganizer

Current preview: **v1.0.32**. License: MIT. Third-party notices and model licenses remain separate.

## Package contents

- Curated source, tests, English README and guides.
- Windows EXE with its complete `_internal` directory.
- Install.cmd / Install.ps1 and Uninstall.cmd / Uninstall.ps1.
- LICENSE, README, CONTRIBUTING, SECURITY, publisher.json, templates and dependency notices.
- Source ZIP and SHA-256 checksums.

Model weights, local caches, personal paths, histories, credentials and demonstration datasets are excluded. Settings stay in `%LOCALAPPDATA%/ModelLibraryOrganizer`.

## Verification

Local regression tests and fresh-settings packaged startup were checked. Windows GitHub Actions checks tests and builds. The uninstaller must not be executed during this verification. No separate-PC or virtual-machine test is claimed.

## Publication

Push reviewed source to main. Publish v1.0.32 as a prerelease with Windows/source ZIPs and checksums. Review the Windows workflow result. A later stable launch is a separate version decision; preview releases are excluded from stable update notifications.

## Build

```powershell
python -m pip install -r requirements.txt pyinstaller==6.22.3
python run_tests.py
python -m PyInstaller --noconfirm ModelLibraryOrganizer.spec
```
