# Publication checklist

Repository: https://github.com/Take-No-Break/ModelLibraryOrganizer
License: MIT. Third-party components keep their own notices.
Prepared preview version: 1.0.11. Application source has not yet been pushed.

## Ready locally

- Curated source with no model weights, caches, personal paths or credentials.
- README, contribution guidance, issue form and MIT license.
- Windows tests/build/startup CI with read-only repository permissions.
- Windows ZIP, source ZIP and SHA256 checksums.
- Git origin points to the intended Take-No-Break repository.

## Publishing sequence

1. Push the prepared local commit to origin/main.
2. Wait for the Windows checks workflow to pass on GitHub.
3. For a preview, create tag/release v1.0.11 as a prerelease and attach the Windows ZIP,
   source ZIP and checksums. Use RELEASE_NOTES.md for the description.
4. Ask a second Windows user to test the package; no VM/second-PC test is claimed.
5. Before the first stable release, choose its version and synchronize the source,
   installer and release tag. The owner's intended first stable version is 1.0.0;
   1.0.11 here is the current development preview, not a stable launch decision.
6. Verify About support links and update notifications after a stable release exists.

## Build

    python -m pip install -r requirements.txt pyinstaller==6.22.3
    python run_tests.py
    python -m PyInstaller --noconfirm ModelLibraryOrganizer.spec

Include LICENSE, README, CONTRIBUTING.md, SECURITY.md, Install.cmd, Install.ps1,
publisher.json, templates and release-licenses beside the EXE/_internal directory.
Settings stay outside the package in LocalAppData/ModelLibraryOrganizer.
