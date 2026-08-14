# Upstream tracking

This repository is a focused downstream variant of [`ckreiling/mcp-server-docker`](https://github.com/ckreiling/mcp-server-docker).

The machine-readable baseline is [`upstream.json`](upstream.json):

- upstream release: `v0.3.0`;
- upstream commit: `57a7df208fdc2362505835f670e53c66f3717c48`;
- upstream package: `mcp-server-docker==0.3.0`;
- downstream release line: `0.3.0+x1pher.1` / tag `v0.3.0-x1pher.1`.

## Downstream behavior delta

The maintained application behavior differs from the upstream baseline in four areas.

### Bounded Docker output

Attached `run_container(detach=false)` results and `fetch_container_logs` results are normalized as UTF-8 with replacement for invalid byte sequences and are bounded to the final 20 KiB. Results include the original byte count and a truncation flag.

Upstream pull request [`ckreiling/mcp-server-docker#61`](https://github.com/ckreiling/mcp-server-docker/pull/61) carries the generic attached-run return-type fix. The 20 KiB bound and bounded log contract remain downstream policy.

### Configuration-preserving container recreation

Upstream `recreate_container` stops and removes the old container and requires the replacement configuration to be supplied again. This downstream variant instead inspects the existing container and recreates it from the inspected configuration, optionally changing only the image.

The implementation preserves the inspected container configuration, `HostConfig`, named/anonymous volume identity, network endpoint configuration and running state where Docker permits. A requested replacement image must already exist locally, so a missing image fails before the existing container is stopped or removed.

If replacement creation fails after the original container has been removed, the server attempts to recreate the original inspected configuration and restore the prior running state. The rollback is best-effort: if both replacement and restoration fail, the tool returns a hard failure containing both error contexts. Container IDs necessarily change during successful recreation or restoration.

This behavior is intentionally maintained downstream rather than treated as an upstream-compatible bug fix.

### Build-intermediate cleanup

`build_image` passes `rm=True` and `forcerm=True` to the Docker SDK so build-intermediate containers are removed after successful and failed builds. The generic change is submitted upstream as [`ckreiling/mcp-server-docker#60`](https://github.com/ckreiling/mcp-server-docker/pull/60).

### Docker filter normalization

Container, image and network filter models are serialized with unset optional values omitted. This avoids Docker SDK behavior changes caused by sending fields such as `label: null`. The generic change is submitted upstream as [`ckreiling/mcp-server-docker#59`](https://github.com/ckreiling/mcp-server-docker/pull/59).


### SSH transport dependency exclusion

Upstream declares Paramiko as a direct dependency so Docker `ssh://` endpoints work out of the box. This downstream release does not package Paramiko because GitHub advisory `GHSA-r374-rxx8-8654` affects released Paramiko versions through `4.0.0` and currently has no patched release. The supported release therefore uses non-SSH Docker endpoints only.

This is a packaging/security delta rather than an MCP tool-surface change. Reconsider it when Paramiko publishes a release containing upstream fix commit `a4489456b6f65281e172380cc4826cee5e851dbb`; do not re-add the dependency merely because a newer version number exists.

## Maintenance-only differences

The repository also contains downstream version metadata, regression tests, public documentation, locked CI, Dependabot configuration, an upstream drift check and a GitHub Release workflow. These are packaging and maintenance differences, not additional MCP capabilities.

No deployment-specific paths, credentials, MCPJungle groups or Homelab configuration belong in this public product repository.

## Update procedure

When the weekly upstream check reports a different upstream release:

1. inspect the new upstream release notes, source, tool schemas and dependency changes;
2. recheck the status and content of upstream pull requests #59, #60 and #61;
3. compare the new upstream source with every downstream behavior section above;
4. recheck `GHSA-r374-rxx8-8654` and whether a released Paramiko version contains fix commit `a4489456b6f65281e172380cc4826cee5e851dbb`;
5. remove any downstream patch that upstream now provides with equivalent accepted semantics;
6. reapply only the still-required downstream behavior to the new exact upstream baseline;
7. update the downstream PEP 440 version and matching `v<upstream>-x1pher.<revision>` release tag contract;
8. regenerate the uv lockfile without widening intentional compatibility bounds unless that widening is separately reviewed;
9. run the complete daemon-free test, lint and reproducible-build contract;
10. perform controlled live Docker acceptance for mutation-sensitive behavior before releasing or deploying the new baseline;
11. update `upstream.json` only after the new baseline and remaining delta are reviewed.

Do not automatically merge upstream source or Dependabot pull requests. Green CI is necessary but is not sufficient approval for a dependency, compatibility or upstream-baseline change.
