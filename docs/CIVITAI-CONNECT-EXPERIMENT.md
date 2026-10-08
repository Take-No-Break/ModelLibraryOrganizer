# Civitai connection experiment

Branch: `experiment/civitai-connect`. Do not merge until real-account testing succeeds.

## What the user does

1. Open **Model inspection → Preview → Connect with Civitai**.
2. Press **Connect with Civitai** in the dialog.
3. Sign in and approve access in the browser.
4. Return to the app and select a model to retry its preview.

## One-time publisher setup

A developer must register Model Library Organizer at https://civitai.com/user/account → OAuth Apps.
Choose a **Public** client (desktop app, no secret).
Register exactly `http://localhost:47831/oauth/callback`.
Allow **UserRead**, **ModelsRead**, **MediaRead** (scope 37).
Enter the resulting public Client ID in the connection dialog. The ID is saved locally; it is not a password.
After testing, the publisher can supply that ID by default in a future version.

## Prototype limits

- Uses authorization code + S256 PKCE, unpredictable state and a loopback-only callback.
- Only Civitai HTTPS /api/v1/ requests receive a bearer token. Authenticated HTTP redirects are rejected.
- General-audience preview filtering remains enabled. Login does not guarantee additional previews.
- Credentials stay in memory only. Sign in again after restart or expiry (up to one hour).
- Disconnect removes local credentials; revoke consent in Civitai Connected Apps.
- No refresh-token persistence, password collection, browser-cookie import or image-CDN authentication.
- Port 47831 must be free; browser consent times out after three minutes.
- Real-provider login is not verified yet because this app has no registered Client ID.
- OAuth authorization on civitai.com does not establish that every civitai.red endpoint accepts the token.

Official specifications: [registration](https://github.com/civitai/civitai-developer-docs/blob/main/site/oauth/register-app.md), [endpoints](https://github.com/civitai/civitai-developer-docs/blob/main/site/oauth/endpoints.md).
