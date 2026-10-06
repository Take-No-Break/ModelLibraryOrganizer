# Publishing, updates and support

Use the public repository's GitHub Releases for downloads and Issues for bug reports. Using the app or checking public releases does not require a GitHub login. Posting an issue requires a GitHub account.

## Distributor setup

1. Configure `Take-No-Break/ModelLibraryOrganizer` in About → Support & Updates.
2. An empty support URL uses repository Issues; optionally configure an HTTPS support form.
3. Export `publisher.json` beside the EXE. Local settings alone are not included in other users' packages.
4. Publish versioned ZIPs and checksums in GitHub Releases. Keep the app version and release tag synchronized.
5. Stable update checks ignore drafts and prereleases. Startup checks are off by default.

## Reports

Saving a report does not send it anywhere. Opening the support page opens the browser; users submit reports themselves. GitHub Issues arrive in this repository. Configure GitHub Watch/email notifications in the owner's GitHub account if desired.

Diagnostic reports omit personal paths, model names, credentials, detailed exception messages, response bodies and images. Always review attachments. Exported model lists and local caches are different from sanitized diagnostics and may contain private paths.

## Offline use

Fully offline mode cannot retrieve updates. Users can check the release page later or run a manual check when online. The app opens a release page; it does not automatically download, overwrite or execute an update.

Extract new Windows ZIPs completely. Preferences and history remain in `%LOCALAPPDATA%/ModelLibraryOrganizer`; never include that directory in public distribution packages.
