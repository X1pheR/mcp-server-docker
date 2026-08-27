import stat
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_canonical_verifier_is_executable_and_reused_by_hosted_workflows():
    verifier = ROOT / "scripts" / "verify.sh"
    assert verifier.is_file()
    assert verifier.stat().st_mode & stat.S_IXUSR

    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
    release = (ROOT / ".github" / "workflows" / "release.yml").read_text()
    assert "./scripts/verify.sh" in ci
    assert "./scripts/verify.sh" in release


def test_ci_and_release_do_not_duplicate_canonical_test_commands():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
    release = (ROOT / ".github" / "workflows" / "release.yml").read_text()
    duplicated_commands = (
        "uv sync --frozen --all-groups",
        "uv run --frozen pytest",
        "uv run --frozen ruff format --check",
        "uv run --frozen ruff check",
    )
    for command in duplicated_commands:
        assert command not in ci
        assert command not in release
