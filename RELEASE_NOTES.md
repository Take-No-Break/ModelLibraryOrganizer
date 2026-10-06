# Windows preview 1.0.8

- Readable SHA256 duplicate tables for new and existing saved reports, distinguishing hard links from independent copies and showing extra storage.
- Full-scan confirmation and original file/folder inventory JSON before scanning. Actual move journals remain required for restoration and are linked to the inventory.
- Contextual restoration action, automatic history refresh and missing-journal reporting.
- Combined Civitai/Hugging Face lookup by default; .com fallback and removal of the separate single-file HF lookup button.
- English About explains SeaArt automation limitations and Tensor.Art website @sha256 search; neither site is automatically queried without a verified public API.

Extract the entire Windows ZIP and run ModelLibraryOrganizer.exe. Keep _internal beside it. Python is not required. Install.cmd optionally installs for the current user.

Models, personal paths, caches and credentials are excluded. No real model files were moved during verification. Windows preview is unsigned. No second-PC/VM or real GPU model inference validation is claimed. Inventory JSON records placement, not model contents; restore uses actual move journals and refuses changed/conflicting files.

Project license: MIT. Third-party components retain their licenses. Repository: https://github.com/Take-No-Break/ModelLibraryOrganizer
