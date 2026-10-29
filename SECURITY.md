# Security policy

MaskLab keeps provider credentials server-side, bounds imports and requests/costs, preserves immutable evidence, and separates owner research from the restricted public demo. Local implementation and live inference have been verified; deployment and public availability remain separate release gates.

Never publish private questions, participant data or provider credentials. Only the operator-approved, explicitly labeled derivatives in `public-evidence/` may be included with source; private originals, workspace databases, the spending ledger and local dotenv files remain excluded. Keep credentials in protected local/server configuration. Exports must omit credentials, host-specific private paths and sensitive connection settings. Imported archives never grant execution or connection permission.

Before EVERY authorized commit run `acp secrets --path /home/asuna/Documents/code/masklab --scope staged`; before pushing require the installed pre-push history scan and an explicit history check when applicable. Fresh clones install with `acp secrets --path /absolute/repo --install`. Gitleaks missing, errors or findings block the operation. Fix sensitive literals, stage fixes and rescan. Never disable hooks or hide findings with a suppression/baseline. Local administrators can override hooks; they are not a server-side authorization boundary.

If a real secret appears in history, stop publication and notify its owner through an established private channel. Rotation/revocation and history rewriting are separate authorized actions. Do not paste secrets into chat, logs or public reports. No dedicated vulnerability-reporting address has been established; use an existing private channel to the owner.
