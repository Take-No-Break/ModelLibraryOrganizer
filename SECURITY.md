# Security and support

Review exported diagnostic reports before sharing them. Never attach API tokens,
passwords, private model weights or your complete application data folder to a public issue.

Model Library Organizer stores classification caches, preferences and reversible file-change
journals locally. Source lookup requests can send model hashes and search names to public
source APIs. Images used for Image to Text are processed in your separately installed ComfyUI.

Repository: https://github.com/Take-No-Break/ModelLibraryOrganizer
For non-sensitive bugs, use its Issues page. Do not post secrets or exploitable security
details publicly; use GitHub private vulnerability reporting if enabled by the owner. Security reports are not uploaded automatically by this app.

## Trust boundaries

Scanning reads metadata and hashes without deserializing tensor weights. Image to Text runs separately in ComfyUI; the PixAI adapter executes Python supplied with the selected model bundle. Only use trusted model bundles and custom nodes. Source hash matching is not a code audit.

Only import move histories you trust. Restoration validates recorded file identity and associated source-TXT paths; histories are not authenticated backups and cannot reverse every external edit. Preview downloads are capped at 20 MB and 40 million pixels before thumbnail decoding.
