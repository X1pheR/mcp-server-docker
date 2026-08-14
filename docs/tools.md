# Tool reference

This document covers the 19 tools exposed by the X1pheR Docker MCP downstream variant based on upstream `v0.3.0`.

Access classes used here are:

- **Read**: intended to inspect Docker state without changing it.
- **Write**: changes Docker or registry state but is not primarily a deletion/replacement operation.
- **Destructive**: deletes or replaces existing Docker state and requires explicit care.

MCP tool annotations are advisory metadata, not an authorization boundary. The Docker daemon remains the actual privilege boundary.

## Containers

| Tool | Access | Important inputs | Side effects and guards |
|---|---|---|---|
| `list_containers` | Read | `all`, optional typed `filters` | Lists containers. Unset optional filter fields are omitted before calling the Docker SDK. |
| `create_container` | Write | `image`, `detach`, `name`, `entrypoint`, `command`, `network`, `environment`, `ports`, `volumes`, `labels`, `auto_remove` | Creates a container but does not start it. The tool surface does not expose privileged mode, capability or device inputs. Environment values and mounts may contain sensitive data. |
| `run_container` | Write | Same creation inputs as `create_container`; `detach` controls attached/detached execution | Creates and starts a container. With `detach=false`, command output is returned as UTF-8-safe structured output bounded to the final 20 KiB with byte-count/truncation metadata. The tool surface does not expose privileged mode, capability or device inputs. |
| `recreate_container` | Destructive | `container_id`; optional replacement `image` | Inspects, stops and removes the existing container, then recreates it while preserving inspected configuration and prior running state. A replacement image must already exist locally. Container ID changes. On replacement failure, automatic restoration of the original inspected configuration is attempted; rollback can itself fail. Existing `HostConfig`, including security-sensitive settings already present, is intentionally preserved. |
| `start_container` | Write | `container_id` | Starts an existing container. Container startup can expose ports, mount host paths and run image-defined processes. |
| `fetch_container_logs` | Read | `container_id`, `tail` (`100` by default or `"all"`) | Reads logs and returns only the final 20 KiB, with original byte count and truncation metadata. Logs can contain secrets even though the operation is read-only. |
| `stop_container` | Write | `container_id` | Stops a running container. This changes service availability but does not delete the container. |
| `remove_container` | Destructive | `container_id`, `force` | Removes a container. `force=true` can remove a running container. Data stored only in the writable container layer is lost. Named volumes are not removed by this tool. |

## Images

| Tool | Access | Important inputs | Side effects and guards |
|---|---|---|---|
| `list_images` | Read | `name`, `all`, optional typed `filters` | Lists local images. Unset optional filter fields are omitted before calling the Docker SDK. |
| `pull_image` | Write | `repository`, optional `tag` (default `latest`) | Contacts a registry through the Docker daemon and adds/updates local image content. Registry authentication is delegated to Docker configuration. |
| `push_image` | Write | `repository`, optional `tag` (default `latest`) | Publishes image content to a registry through the Docker daemon. This is an external side effect and can disclose image contents to the selected registry. |
| `build_image` | Write | build-context `path`, output `tag`, optional `dockerfile` | Sends the build context to Docker and executes Dockerfile build steps. The maintained variant passes `rm=True` and `forcerm=True` to clean intermediate containers on success and failure. Builds can access networks or secrets depending on Docker/build configuration outside this tool. |
| `remove_image` | Destructive | image ID/name, `force` | Removes local image references/content when Docker permits. `force=true` can remove conflicting references. |

## Networks

| Tool | Access | Important inputs | Side effects and guards |
|---|---|---|---|
| `list_networks` | Read | optional typed `filters` | Lists Docker networks. Unset optional filter fields are omitted before calling the Docker SDK. |
| `create_network` | Write | `name`, optional `driver` (default `bridge`), `internal`, `labels` | Creates a Docker network. Driver behavior and host networking effects are controlled by Docker. |
| `remove_network` | Destructive | network ID/name | Removes a Docker network when Docker permits. Attached workloads can prevent removal or lose connectivity if the surrounding state changes concurrently. |

## Volumes

| Tool | Access | Important inputs | Side effects and guards |
|---|---|---|---|
| `list_volumes` | Read | none | Lists Docker volumes. Volume contents are not read by this tool. |
| `create_volume` | Write | `name`, optional `driver` (default `local`), `labels` | Creates a Docker volume. Driver-specific behavior is delegated to Docker. |
| `remove_volume` | Destructive | `volume_name`, `force` | Removes a Docker volume when Docker permits. Volume data is permanently lost. `force=true` requests forced removal where supported by the Docker SDK/daemon. |

## Prompt and resources

The server also exposes the upstream `docker_compose` prompt. It asks the client/model to plan and apply a multi-container Docker project using the available tools. The prompt is not an authorization mechanism; clients should still enforce their own confirmation policy for mutation-capable tools.

Two resource templates provide container data by ID or name:

| Resource | Type | Security implication |
|---|---|---|
| `docker://containers/{container_id}/logs` | `text/plain` | Container logs can contain credentials or application data. Resource output is separate from the bounded `fetch_container_logs` tool contract. |
| `docker://containers/{container_id}/stats` | `application/json` | Exposes runtime resource statistics for the selected container. |

## Deployment security

The server uses `docker.from_env()` and therefore inherits the authority of the configured Docker endpoint and its credentials. A local Docker socket is effectively a host-root control channel. A remote non-SSH Docker endpoint can be equally privileged on the remote host. Docker `ssh://` endpoints are deliberately not supported by the maintained `0.3.0+x1pher.1` dependency set while released Paramiko versions remain affected by `GHSA-r374-rxx8-8654`.

Use external policy to separate read-only consumer groups from mutation-capable consumers. A read-only MCP allowlist is meaningful; mounting `/var/run/docker.sock` read-only is not sufficient to make Docker API calls read-only.
