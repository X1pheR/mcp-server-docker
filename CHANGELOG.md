# Changelog

This file records user-visible changes to the maintained downstream `mcp-server-docker` product. Upstream-baseline changes are also documented in [UPSTREAM.md](UPSTREAM.md).

## Unreleased

- Added public OpenSSF Scorecard reporting and protected-branch repository controls.
- Future releases publish signed GitHub/Sigstore build provenance alongside checksums and reproducible wheel artifacts.
- Added explicit contribution and private vulnerability-reporting routes.

## 0.3.0-x1pher.1 - 2026-08-14

Initial public downstream release based on upstream `v0.3.0`.

- Added bounded UTF-8-safe attached run/log output with truncation metadata.
- Added configuration-preserving `recreate_container` behavior with best-effort restoration on replacement failure.
- Added forced intermediate-container cleanup for image builds and omitted unset Docker filter values.
- Deliberately excluded Paramiko and Docker `ssh://` transport while released Paramiko versions remained affected by `GHSA-r374-rxx8-8654`.
- Published a reproducible wheel with `SHA256SUMS`; production consumption uses the immutable release asset.
