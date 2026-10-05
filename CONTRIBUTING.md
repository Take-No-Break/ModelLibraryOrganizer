# Contributing

Bug reports, documentation improvements and pull requests are welcome.
Please describe the problem, proposed change and how you verified it.
Never include personal paths, access tokens, model weights or local application caches.
Review diagnostic reports before posting them publicly.

## Development

Use Python 3.12 on Windows:

    python -m pip install -r requirements.txt
    python run_tests.py

For a Windows package:

    python -m pip install pyinstaller==6.22.3
    python -m PyInstaller --noconfirm ModelLibraryOrganizer.spec

Test file changes and restore operations on disposable copies. Keep user approval
before moving models, preserve recovery journals, and avoid overwriting existing data.
New UI text should support the existing language system.

## License

By submitting a contribution, you agree that your contribution can be distributed
under this project's MIT license. Preserve notices for any third-party code.
MIT does not require submitting your modifications upstream; we welcome it voluntarily.
