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

This behavior remains an unapproved downstream variation. The accepted upstream-first standard requires resolution of [upstream issue #62](https://github.com/ckreiling/mcp-server-docker/issues/62) through an upstream-compatible PR, or a separately operator-approved exact-scope product ADR. No such PR or approval is recorded.

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

## Machine-readable downstream patch register

This inline register is the product-owned logical-patch projection used by SDLC-09 structural verification. Its state does not replace current GitHub issue/PR verification, an actual upstream-compatible tested diff, or any required operator-approved product ADR. Unlinked rows are explicitly nonconformant; no historical fork behavior has been grandfathered. Cross-product integration and release actions remain gated separately. Patch scope and local commit mappings require further semantic review before external contribution.

<!-- SDLC-UPSTREAM-REGISTER:1 -->
```json
{
  "schema_version": 1,
  "upstream": "ckreiling/mcp-server-docker",
  "baseline": "v0.3.0",
  "patches": [
    {
      "id": "DK-P01",
      "kind": "upstream",
      "scope": "Attached Docker container run result type normalization",
      "local_commits": [
        "2f6020b"
      ],
      "checked_on": "2026-10-10",
      "issue": "https://github.com/ckreiling/mcp-server-docker/issues/69",
      "pr": "https://github.com/ckreiling/mcp-server-docker/pull/61",
      "pr_state": "open"
    },
    {
      "id": "DK-P02",
      "kind": "upstream",
      "scope": "Bounded Docker output and deterministic truncation metadata",
      "local_commits": [
        "2f6020b"
      ],
      "checked_on": "2026-10-10",
      "issue": null,
      "pr": null
    },
    {
      "id": "DK-P03",
      "kind": "upstream",
      "scope": "Configuration-preserving Docker container recreation with rollback safeguards",
      "local_commits": [
        "2f6020b"
      ],
      "checked_on": "2026-10-10",
      "issue": "https://github.com/ckreiling/mcp-server-docker/issues/62",
      "pr": null
    },
    {
      "id": "DK-P04",
      "kind": "upstream",
      "scope": "Docker build intermediate container cleanup",
      "local_commits": [
        "2f6020b"
      ],
      "checked_on": "2026-10-10",
      "issue": "https://github.com/ckreiling/mcp-server-docker/issues/68",
      "pr": "https://github.com/ckreiling/mcp-server-docker/pull/60",
      "pr_state": "open"
    },
    {
      "id": "DK-P05",
      "kind": "upstream",
      "scope": "Omit unset values when normalizing Docker SDK filters",
      "local_commits": [
        "2f6020b"
      ],
      "checked_on": "2026-10-10",
      "issue": "https://github.com/ckreiling/mcp-server-docker/issues/67",
      "pr": "https://github.com/ckreiling/mcp-server-docker/pull/59",
      "pr_state": "open"
    },
    {
      "id": "DK-P06",
      "kind": "upstream",
      "scope": "Paramiko vulnerability mitigation by removing optional SSH transport dependency",
      "local_commits": [
        "2f6020b"
      ],
      "checked_on": "2026-10-10",
      "issue": null,
      "pr": null
    },
    {
      "id": "DK-P07",
      "kind": "upstream",
      "scope": "Source verification, release packaging and downstream publication",
      "local_commits": [
        "49a43c7",
        "f56fed0"
      ],
      "checked_on": "2026-10-10",
      "issue": null,
      "pr": null
    }
  ]
}
```

## Convergence lifecycle

Verify existing upstream issues and PRs, current default-branch equivalence, and source-owned regression evidence before submitting missing contributions. A PR that is closed without merge is nonconformant, and a merged PR is not automatically present in an immutable official release. Remove a downstream patch only on a tested candidate against a suitable released upstream artifact. Retire the fork only after verified patch elimination, accepted distribution/ADR disposition, rollback readiness, consumer parity, and separate operator approval for production/retirement.
