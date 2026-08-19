# Contributing

Contributions are welcome through GitHub issues and pull requests.

## Before opening a change

- Use GitHub Issues for reproducible bugs and focused feature proposals.
- Use the private reporting process in [SECURITY.md](SECURITY.md) for suspected vulnerabilities.
- Keep changes narrowly scoped; this repository intentionally tracks one upstream Docker MCP baseline plus explicit downstream deltas.
- Never include Docker credentials, registry credentials, TLS material, container environment values, private image names, or other sensitive deployment data in issues, fixtures, tests, logs, or commits.

## Development setup

Use Python 3.12 and the committed lock file:

```bash
uv sync --frozen --all-groups
uv run --frozen pytest -q
uv run --frozen ruff format --check src tests
uv run --frozen ruff check src tests
uv build
```

## Change requirements

- Add or update automated tests for downstream behavior changes and bug fixes where a regression test is practical.
- Preserve the documented 19-tool Docker MCP surface unless a product decision explicitly owns a surface change.
- Update `UPSTREAM.md` and `upstream.json` when adopting a new upstream baseline or changing tracked upstream pull-request relationships.
- Update `docs/tools.md` when the public tool contract changes.
- Update README or security documentation when Docker Engine compatibility, supported transports, downstream behavior, or trust boundaries change.
- Add a concise entry under `Unreleased` in [CHANGELOG.md](CHANGELOG.md) for user-visible changes.
- Keep dependency changes within declared compatibility ranges unless the pull request explicitly owns a compatibility change.

A pull request is ready for review when daemon-free CI-equivalent verification passes. Changes to Docker runtime behavior also require the separately controlled live-engine acceptance used by the release process.
