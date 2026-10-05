# Windows preview 1.0.7

Model Library Organizer helps inspect, review and organize local AI model libraries.

- Model identification from structure, metadata and public source hashes.
- Review destinations and hard links before applying changes; restore from history.
- In-app previews and checkpoint/LoRA compatibility estimates.
- Editable Image to Text ComfyUI templates and batch caption editing.
- Japanese, English, Spanish, Chinese (Simplified/Traditional), Thai, German and Brazilian Portuguese UI.
- MIT project license; contributions are welcome.

## Installation

Download the Windows-x64-Preview ZIP, extract everything, and run
ModelLibraryOrganizer.exe. Keep _internal beside it. Python is not required.
Install.cmd optionally installs for the current user without administrator rights.

## Known limits

Windows package is unsigned. No second-PC/VM validation is claimed.
Compatibility is an estimate, not a guarantee of loading or image quality.
PixAI inference was previously verified; other caption adapters have schema tests,
but their actual GPU inference is not yet verified. Model weights are not bundled.
Update notifications use stable GitHub Releases; previews are excluded.
