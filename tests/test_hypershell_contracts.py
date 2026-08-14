from __future__ import annotations

from copy import deepcopy
from unittest.mock import Mock, patch

import pytest
from docker.errors import ImageNotFound, NotFound
from docker.models.containers import Container

from mcp_server_docker.server import (
    MAX_TEXT_BYTES,
    _bounded_log_result,
    _bounded_text,
    _build_recreate_payload,
    _json_safe,
    _recreate_existing_container,
    _run_result,
)


def _container_attrs(*, running: bool = True) -> dict:
    return {
        "Image": "sha256:old-image",
        "Config": {
            "Hostname": "abc123def456",
            "Domainname": "",
            "User": "1000:1000",
            "Env": ["MODE=test"],
            "Cmd": ["serve"],
            "Healthcheck": {"Test": ["CMD", "healthcheck"], "Interval": 30_000_000_000},
            "Image": "example:old",
            "Labels": {"app": "example", "com.docker.compose.project": "test-project"},
            "ExposedPorts": {"8080/tcp": {}},
            "Volumes": {"/cache": {}},
            "WorkingDir": "/app",
            "Entrypoint": ["/entrypoint"],
        },
        "HostConfig": {
            "NetworkMode": "prod",
            "Binds": ["/srv/example:/data:ro"],
            "Mounts": [],
            "PortBindings": {
                "8080/tcp": [{"HostIp": "127.0.0.1", "HostPort": "18080"}]
            },
            "RestartPolicy": {"Name": "unless-stopped", "MaximumRetryCount": 0},
            "AutoRemove": False,
        },
        "Mounts": [
            {
                "Type": "bind",
                "Source": "/srv/example",
                "Destination": "/data",
                "RW": False,
            },
            {
                "Type": "volume",
                "Name": "example-cache-volume",
                "Destination": "/cache",
                "RW": True,
            },
        ],
        "NetworkSettings": {
            "Networks": {
                "prod": {
                    "IPAMConfig": {"IPv4Address": "172.20.0.25"},
                    "Aliases": ["example", "example-service"],
                    "NetworkID": "runtime-network-id",
                    "EndpointID": "runtime-endpoint-id",
                    "IPAddress": "172.20.0.25",
                }
            }
        },
        "State": {"Running": running, "Status": "running" if running else "exited"},
    }


def _mock_container(*, running: bool = True) -> Mock:
    container = Mock(spec=Container)
    container.id = "abc123def4567890"
    container.name = "example-container"
    container.attrs = _container_attrs(running=running)
    return container


def test_output_normalization_and_bounds():
    assert _bounded_text(b"ok\xffend") == {
        "text": "ok\ufffdend",
        "truncated": False,
        "bytes": 6,
    }
    raw = b"a" * (MAX_TEXT_BYTES + 9)
    bounded = _bounded_text(raw)
    assert bounded["truncated"] is True
    assert bounded["bytes"] == MAX_TEXT_BYTES + 9
    assert len(bounded["text"].encode()) == MAX_TEXT_BYTES
    assert _bounded_log_result(b"one\ntwo")["logs"] == ["one", "two"]
    nested = _json_safe({"logs": [b"one", {"two": bytearray(b"two")}]})
    assert nested["logs"][0]["text"] == "one"
    assert nested["logs"][1]["two"]["text"] == "two"
    attached = _run_result(b"hello", detach=False)
    assert attached["mode"] == "attached"
    assert attached["output"]["text"] == "hello"
    with pytest.raises(TypeError):
        _run_result(b"unexpected", detach=True)


def test_recreate_payload_preserves_configuration():
    container = _mock_container()
    original = deepcopy(container.attrs)
    payload = _build_recreate_payload(container, "example:new")
    assert payload["Image"] == "example:new"
    assert payload["Hostname"] == ""
    assert payload["Env"] == ["MODE=test"]
    assert payload["Healthcheck"]["Test"] == ["CMD", "healthcheck"]
    assert payload["HostConfig"]["RestartPolicy"]["Name"] == "unless-stopped"
    assert "example-cache-volume:/cache:rw" in payload["HostConfig"]["Binds"]
    endpoint = payload["NetworkingConfig"]["EndpointsConfig"]["prod"]
    assert endpoint["IPAMConfig"]["IPv4Address"] == "172.20.0.25"
    assert endpoint["Aliases"] == ["example", "example-service"]
    assert (
        "NetworkID" not in endpoint
        and "EndpointID" not in endpoint
        and "IPAddress" not in endpoint
    )
    assert container.attrs == original


def test_existing_mount_target_is_not_duplicated():
    container = _mock_container()
    container.attrs["HostConfig"]["Mounts"] = [
        {"Type": "volume", "Source": "example-cache-volume", "Target": "/cache"}
    ]
    payload = _build_recreate_payload(container, "example:new")
    assert "example-cache-volume:/cache:rw" not in payload["HostConfig"]["Binds"]


@patch(
    "mcp_server_docker.server.docker_to_dict",
    return_value={"status": "recreated", "configuration_preserved": True},
)
def test_recreate_success_preserves_running_state(converter: Mock):
    original = _mock_container(running=True)
    replacement = _mock_container(running=True)
    replacement.id = "new-container-id"
    client = Mock()
    client.containers.get.side_effect = [original, replacement]
    client.api.create_container_from_config.return_value = {"Id": replacement.id}
    result = _recreate_existing_container(client, "example-container", "example:new")
    client.images.get.assert_called_once_with("example:new")
    original.reload.assert_called_once_with()
    original.stop.assert_called_once_with()
    original.remove.assert_called_once_with()
    replacement.start.assert_called_once_with()
    replacement.reload.assert_called_once_with()
    assert result["configuration_preserved"] is True
    converter.assert_called_once()


@patch("mcp_server_docker.server.docker_to_dict", return_value={"status": "recreated"})
def test_auto_remove_container_can_disappear_during_stop(converter: Mock):
    original = _mock_container(running=True)
    original.attrs["HostConfig"]["AutoRemove"] = True
    original.remove.side_effect = NotFound("already removed")
    replacement = _mock_container(running=True)
    replacement.id = "new-container-id"
    client = Mock()
    client.containers.get.side_effect = [original, replacement]
    client.api.create_container_from_config.return_value = {"Id": replacement.id}
    _recreate_existing_container(client, "example-container")
    replacement.start.assert_called_once_with()
    converter.assert_called_once()


def test_missing_image_fails_before_stop_or_remove():
    original = _mock_container(running=True)
    client = Mock()
    client.containers.get.return_value = original
    client.images.get.side_effect = ImageNotFound("missing")
    with pytest.raises(ImageNotFound):
        _recreate_existing_container(client, "example-container", "missing:image")
    original.stop.assert_not_called()
    original.remove.assert_not_called()
    client.api.create_container_from_config.assert_not_called()


def test_failed_recreate_restores_original_configuration():
    original = _mock_container(running=True)
    restored = _mock_container(running=True)
    restored.id = "restored-container-id"
    client = Mock()
    client.containers.get.side_effect = [original, restored]
    client.api.create_container_from_config.side_effect = [
        RuntimeError("create failed"),
        {"Id": restored.id},
    ]
    with pytest.raises(RuntimeError, match="restored successfully"):
        _recreate_existing_container(client, "example-container", "example:new")
    assert client.api.create_container_from_config.call_count == 2
    rollback = client.api.create_container_from_config.call_args_list[1].args[0]
    assert rollback["Image"] == "sha256:old-image"
    restored.start.assert_called_once_with()
