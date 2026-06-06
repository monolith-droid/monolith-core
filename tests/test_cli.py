from __future__ import annotations

from pathlib import Path

from monolith_core.cli import main, validate_root


ROOT = Path("examples/synthetic-vault")


def test_validate_root_passes_for_synthetic_vault() -> None:
    result = validate_root(ROOT)
    assert result["passed"] is True
    assert result["card_count"] == 2
    assert result["blockers"] == []


def test_pack_command_passes() -> None:
    code = main([
        "pack",
        "--index",
        "examples/synthetic-vault/index.json",
        "--pack",
        "examples/synthetic-vault/context-pack.json",
    ])
    assert code == 0


def test_branch_return_command_passes() -> None:
    code = main([
        "branch-return-check",
        "--report",
        "examples/synthetic-vault/branch-return.json",
    ])
    assert code == 0


def test_curate_dry_run_writes_report(tmp_path: Path) -> None:
    out = tmp_path / "curator-report.json"
    code = main([
        "curate-dry-run",
        "--root",
        "examples/synthetic-vault",
        "--out",
        str(out),
    ])
    assert code == 0
    assert out.exists()
