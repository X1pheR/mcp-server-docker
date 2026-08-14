# Security policy

## Reporting a vulnerability

Please report vulnerabilities through GitHub private vulnerability reporting when it is available for this repository. Do not include credentials, Docker configuration, container environment values, private image names or other secrets in a public issue.

If private vulnerability reporting is unavailable, open a public issue containing only enough non-sensitive information to request a private follow-up channel.

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

Until the first immutable X1pheR release is published, only the current reviewed `main` revision is maintained. After releases begin, the latest accepted X1pheR GitHub Release is the supported line unless a release note states otherwise.

Upstream-only issues that are unchanged by this downstream variant should also be reported to the upstream project when appropriate.
