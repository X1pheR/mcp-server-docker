#!/usr/bin/env sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
PYTHON_IMAGE="${VERIFY_PYTHON_IMAGE:-python:3.12-slim-bookworm}"
UV_VERSION="${VERIFY_UV_VERSION:-0.12.4}"
TMP_DIR=""
FAKE_DOCKER_PID=""

cleanup() {
  if [ -n "${FAKE_DOCKER_PID}" ]; then
    kill "${FAKE_DOCKER_PID}" 2>/dev/null || true
    wait "${FAKE_DOCKER_PID}" 2>/dev/null || true
  fi
  if [ -n "${TMP_DIR}" ] && [ -d "${TMP_DIR}" ]; then
    rm -rf -- "${TMP_DIR}"
  fi
}
trap cleanup EXIT HUP INT TERM

if [ "${VERIFY_INNER:-0}" != "1" ]; then
  command -v docker >/dev/null 2>&1 || {
    echo "Docker is required for repository verification" >&2
    exit 1
  }
  command -v python3 >/dev/null 2>&1 || {
    echo "python3 is required for the hermetic Docker API fixture" >&2
    exit 1
  }
  command -v git >/dev/null 2>&1 || {
    echo "git is required for repository verification" >&2
    exit 1
  }

  TMP_DIR="$(mktemp -d)"
  FAKE_SOCKET="${TMP_DIR}/docker.sock"
  python3 "${ROOT}/tests/fake_docker_version_api.py" "${FAKE_SOCKET}" &
  FAKE_DOCKER_PID=$!
  i=0
  while [ ! -S "${FAKE_SOCKET}" ]; do
    i=$((i + 1))
    if [ "${i}" -gt 100 ]; then
      echo "fake Docker API socket did not become ready" >&2
      exit 1
    fi
    sleep 0.05
  done

  docker run --rm \
    --env HOME=/tmp/home \
    --env PIP_ROOT_USER_ACTION=ignore \
    --env PYTHONDONTWRITEBYTECODE=1 \
    --env RUFF_CACHE_DIR=/tmp/ruff-cache \
    --env UV_CACHE_DIR=/tmp/uv-cache \
    --env VERIFY_INNER=1 \
    --env "VERIFY_UV_VERSION=${UV_VERSION}" \
    --volume "${ROOT}:/source:ro" \
    --volume "${FAKE_SOCKET}:/var/run/docker.sock" \
    "${PYTHON_IMAGE}" \
    /bin/sh -c 'set -eu; python -m pip install --disable-pip-version-check --no-cache-dir "uv==${VERIFY_UV_VERSION}" >/dev/null; mkdir -p /tmp/repository; cp -a /source/. /tmp/repository/; cd /tmp/repository; exec ./scripts/verify.sh'

  git -C "${ROOT}" diff --check
  exit 0
fi

command -v uv >/dev/null 2>&1 || {
  echo "uv is required inside the verification environment" >&2
  exit 1
}

TMP_DIR="$(mktemp -d)"
uv sync --frozen --all-groups

uv run --frozen python - <<'PY'
import importlib.metadata
import tomllib
from mcp_server_docker._version import __version__

with open("pyproject.toml", "rb") as handle:
    project = tomllib.load(handle)["project"]["version"]
installed = importlib.metadata.version("mcp-server-docker")
assert installed == project == __version__, (installed, project, __version__)
PY

uv run --frozen pytest -q -p no:cacheprovider
uv run --frozen ruff format --check src tests
uv run --frozen ruff check src tests
uv build --out-dir "${TMP_DIR}/dist"
