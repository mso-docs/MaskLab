# Security policy

MaskLab's application is not implemented yet. The release specification requires server-side credentials, bounded imports, immutable evidence, request/cost limits and separation of owner research mode from public demo mode.

Never publish private questions, participant data or provider credentials. Keep credentials in protected local/server configuration. Exports must omit credentials, host-specific private paths and sensitive connection settings. Imported archives never grant execution or connection permission.

Before EVERY authorized commit run `acp secrets --path /home/asuna/Documents/code/masklab --scope staged`; before pushing require the installed pre-push history scan and an explicit history check when applicable. Fresh clones install with `acp secrets --path /absolute/repo --install`. Gitleaks missing, errors or findings block the operation. Fix sensitive literals, stage fixes and rescan. Never disable hooks or hide findings with a suppression/baseline. Local administrators can override hooks; they are not a server-side authorization boundary.

If a real secret appears in history, stop publication and notify its owner through an established private channel. Rotation/revocation and history rewriting are separate authorized actions. Do not paste secrets into chat, logs or public reports. No dedicated vulnerability-reporting address has been established; use an existing private channel to the owner.
