# Docker MCP Server

A community-maintained downstream variant of [ckreiling/mcp-server-docker](https://github.com/ckreiling/mcp-server-docker) that keeps the upstream Docker MCP surface while adding a small set of safety and compatibility changes used in maintained deployments.

This repository is independently maintained by X1pheR. It is not affiliated with or endorsed by the upstream maintainer, Docker, Inc., or the Model Context Protocol project.

## Why this variant exists

The maintained baseline is upstream `v0.3.0` at commit `57a7df208fdc2362505835f670e53c66f3717c48`. The downstream behavior differs in four areas:

- attached `run_container` output and `fetch_container_logs` output are UTF-8-safe and bounded to the final 20 KiB, with truncation metadata;
- `recreate_container` rebuilds an existing container from inspected configuration, preserves its running state and attempts automatic restoration if replacement creation fails;
- `build_image` forces cleanup of intermediate build containers on successful and failed builds;
- optional Docker SDK filter fields with no value are omitted instead of being sent as `null`.

The generic filter, build-cleanup and attached-run fixes have also been submitted upstream. The configuration-preserving recreate behavior and output-size policy remain intentional downstream policy. See [`UPSTREAM.md`](UPSTREAM.md) for the exact baseline, tracked upstream pull requests and update procedure.

## Requirements

- Python 3.12 or newer.
- A Docker Engine reachable through the Python Docker SDK `from_env()` configuration.
- Docker SDK `7.1.0` or newer within the dependency contract in `pyproject.toml` and the reviewed lockfile.

Docker Engine `29.6.2` is the current live deployment target for this release line. CI is daemon-free; final release acceptance requires controlled live validation against that engine. Broader Docker Engine compatibility is not claimed.

## Install and run

The X1pheR downstream release is distributed through GitHub Releases, not PyPI. Running `uvx mcp-server-docker` without `--from` installs the upstream PyPI package and does **not** install this variant.

For development or pre-release review, clone the repository and use the locked environment:

```bash
git clone https://github.com/X1pheR/mcp-server-docker.git
cd mcp-server-docker
uv sync --frozen --all-groups
uv run mcp-server-docker
```

After an accepted X1pheR release is published, pin production use to that immutable release asset:

```bash
uvx --python 3.12 \
  --from "https://github.com/X1pheR/mcp-server-docker/releases/download/<release-tag>/<wheel-file>" \
  mcp-server-docker
```

Example MCP client configuration using a reviewed GitHub Release wheel:

```json
{
  "mcpServers": {
    "docker": {
      "command": "uvx",
      "args": [
        "--python",
        "3.12",
        "--from",
        "https://github.com/X1pheR/mcp-server-docker/releases/download/<release-tag>/<wheel-file>",
        "mcp-server-docker"
      ]
    }
  }
}
```

Do not replace `<release-tag>` and `<wheel-file>` with a mutable branch URL for production use.

### Run in Docker

For local evaluation, build the repository checkout and mount the Docker socket:

```bash
docker build -t mcp-server-docker .
docker run --rm -i \
  -v /var/run/docker.sock:/var/run/docker.sock \
  mcp-server-docker
```

A Docker socket mount grants the server control over the Docker daemon. Treat that capability as host-root equivalent even if the socket itself is mounted read-only.

## Configuration

The server uses `docker.from_env()`. Standard Docker SDK environment variables therefore define the daemon connection, including `DOCKER_HOST` and the Docker TLS variables where applicable.

Example for a remote Docker daemon over SSH:

```json
{
  "mcpServers": {
    "docker": {
      "command": "uvx",
      "args": [
        "--python",
        "3.12",
        "--from",
        "https://github.com/X1pheR/mcp-server-docker/releases/download/<release-tag>/<wheel-file>",
        "mcp-server-docker"
      ],
      "env": {
        "DOCKER_HOST": "ssh://docker-user@docker-host.example.com"
      }
    }
  }
}
```

SSH keys, Docker registry credentials and TLS material remain external deployment concerns. Do not commit them to this repository or put secret values in example configuration.

## MCP surface

The server exposes the same 19 tool names as upstream `v0.3.0`:

| Capability | Tools |
|---|---|
| Read | `list_containers`, `fetch_container_logs`, `list_images`, `list_networks`, `list_volumes` |
| Write | `create_container`, `run_container`, `start_container`, `stop_container`, `pull_image`, `push_image`, `build_image`, `create_network`, `create_volume` |
| Destructive | `recreate_container`, `remove_container`, `remove_image`, `remove_network`, `remove_volume` |

See [`docs/tools.md`](docs/tools.md) for the complete tool reference, including important inputs, side effects, guards and security implications.

The server also exposes the upstream `docker_compose` prompt and two resource templates:

- `docker://containers/{container_id}/logs`
- `docker://containers/{container_id}/stats`

## Security model

Docker daemon access is the primary authorization boundary. The MCP server does not add user authentication or an authorization layer around Docker operations. Restrict both daemon access and which MCP clients can invoke mutation-capable tools.

`create_container` and `run_container` do not expose inputs for privileged mode, added capabilities or device mappings. `recreate_container` is different: it intentionally preserves the inspected `HostConfig` of an existing container, so security-sensitive settings already present on that container can be preserved during recreation.

Container environment variables and Docker inspect data can expose secrets to the MCP client or model. Prefer an external secret-delivery mechanism rather than placing long-lived credentials in tool arguments.

Image pulls and pushes can contact external registries. Image builds execute Dockerfile instructions through the configured daemon. Review images, build contexts, port bindings, mounts and remote registry targets before allowing write-capable tool use.

See [`SECURITY.md`](SECURITY.md) for vulnerability reporting and supported-version policy.

## Compatibility and versioning

The first maintained downstream release line is based on upstream `0.3.0`. Downstream package versions use PEP 440 local version identifiers such as `0.3.0+x1pher.1`; corresponding GitHub release tags use `v0.3.0-x1pher.1`.

A new upstream release is not supported automatically. It must be reviewed, the still-required downstream delta must be reapplied or removed explicitly, and the full acceptance path must pass before the baseline changes.

Accepted GitHub Release tags and assets are immutable by maintenance policy. Releases publish a reproducible wheel plus `SHA256SUMS`; GitHub provides the source snapshot for the same tag. This repository does not publish the downstream package to PyPI.

## Development

Run the complete daemon-free verification locally with:

```bash
uv sync --frozen --all-groups
uv run --frozen pytest -q
uv run --frozen ruff format --check src tests
uv run --frozen ruff check src tests
uv build
```

CI uses the same locked dependency graph and build contract. Dependabot refreshes the uv lockfile within declared compatibility ranges and tracks GitHub Actions revisions; dependency pull requests remain review-required and are never accepted solely because CI is green.

A weekly upstream check reports when the upstream release differs from [`upstream.json`](upstream.json). It never merges upstream source automatically.

## License

This downstream variant is distributed under the upstream GNU General Public License v3.0. See [`LICENSE`](LICENSE). Upstream project ownership and governance remain with Christian Kreiling and the upstream repository; this repository maintains only the documented downstream delta.
