# Security policy

## Reporting a vulnerability

Please report vulnerabilities through [GitHub private vulnerability reporting](https://github.com/X1pheR/mcp-server-docker/security/advisories/new). Do not include credentials, Docker configuration, container environment values, private image names or other secrets in a public issue.

If private vulnerability reporting is unexpectedly unavailable, open a public issue containing only enough non-sensitive information to request a private follow-up channel.

## Scope

Security reports are especially relevant when they involve:

- unintended Docker mutation or deletion;
- unsafe loss or alteration of configuration during `recreate_container`;
- bypasses that expose privileged Docker options through create/run inputs;
- unbounded or secret-bearing tool output;
- dependency vulnerabilities exploitable through the MCP server;
- behavior introduced by the documented downstream delta.

Docker socket access is intentionally powerful and is not itself a vulnerability. A process with Docker daemon access should be treated as having host-root-equivalent control.

The maintained `0.3.0+x1pher.1` dependency set intentionally excludes Paramiko and therefore does not support Docker `ssh://` endpoints. This avoids shipping released Paramiko versions affected by `GHSA-r374-rxx8-8654` while no patched release exists.

`recreate_container` intentionally preserves the inspected `HostConfig` of an existing container, including security-sensitive settings already present there. The tool does not provide new inputs to add those settings, but their preservation during recreation is expected behavior.

## Supported version

The latest accepted X1pheR GitHub Release is the supported public line unless a release note states otherwise. Security fixes are developed on the reviewed `main` branch and released through the normal downstream release lifecycle.

Upstream-only issues that are unchanged by this downstream variant should also be reported to the upstream project when appropriate.

## Dependency and code security

The repository uses a committed uv lock file, full-SHA-pinned GitHub Actions, daemon-free CI/package verification, Dependabot, upstream release tracking and OpenSSF Scorecard. Public-release acceptance also requires applicable GitHub-native dependency alerts, secret scanning with push protection and CodeQL code scanning to be reviewed and green before a release is published.

These controls supplement rather than replace review of the documented downstream delta and controlled live Docker Engine acceptance for runtime-behavior changes.
