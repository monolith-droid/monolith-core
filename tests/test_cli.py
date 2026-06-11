from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path

from monolith_core.cli import main, score_root, validate_root


ROOT = Path("examples/synthetic-vault")
DOCS = Path("docs")


def test_validate_root_passes_for_synthetic_vault() -> None:
    result = validate_root(ROOT)
    assert result["passed"] is True
    assert result["card_count"] == 2
    assert result["blockers"] == []


def test_synthetic_fixture_uses_stable_id_prefixes() -> None:
    result = validate_root(ROOT)
    assert result["status"] == "valid"

    index = json.loads((ROOT / "index.json").read_text(encoding="utf-8"))
    context_pack = json.loads((ROOT / "context-pack.json").read_text(encoding="utf-8"))
    branch_return = json.loads((ROOT / "branch-return.json").read_text(encoding="utf-8"))

    assert index["index_id"] == "index-synthetic-core"
    assert context_pack["pack_id"] == "pack-monolith-core-mvp"
    assert branch_return["branch_id"] == "branch-synthetic-oss-maintainer"
    assert all(entry["card_id"].startswith("card-") for entry in index["entries"])
    assert all(card_id.startswith("card-") for card_id in context_pack["card_ids"])
    assert all(card_id.startswith("card-") for card_id in branch_return["card_refs"])


def test_synthetic_cards_include_freshness_metadata() -> None:
    for card_path in sorted((ROOT / "cards").glob("*.json")):
        card = json.loads(card_path.read_text(encoding="utf-8"))
        assert card["last_reviewed"] == "2026-06-01"
        assert card["review_interval_days"] == 30


def test_invalid_card_id_fails_validation(tmp_path: Path) -> None:
    fixture = tmp_path / "synthetic-vault"
    shutil.copytree(ROOT, fixture)
    card_path = fixture / "cards" / "card-agent-memory.json"
    card = json.loads(card_path.read_text(encoding="utf-8"))
    card["card_id"] = "Card_AgentMemory"
    card_path.write_text(json.dumps(card), encoding="utf-8")

    code = main(["validate", "--root", str(fixture)])
    assert code == 1


def test_obsidian_workflow_docs_preserve_public_boundary() -> None:
    body = (DOCS / "obsidian-workflow.md").read_text(encoding="utf-8")
    assert "examples/synthetic-vault/" in body
    assert "card-agent-memory" in body
    assert "index-synthetic-core" in body
    assert "pack-monolith-core-mvp" in body
    assert "Private Adapter Boundary" in body
    assert "Public MONOLITH Core should remain useful without any private data" in body


def test_memory_scorecard_fixture_matches_score_command() -> None:
    fixture = json.loads((ROOT / "scorecard.json").read_text(encoding="utf-8"))
    result = score_root(ROOT, as_of=date(2026, 6, 11))
    assert result == fixture


def test_score_command_passes() -> None:
    code = main([
        "score",
        "--root",
        "examples/synthetic-vault",
        "--as-of",
        "2026-06-11",
    ])
    assert code == 0


def test_score_command_detects_missing_freshness_metadata(tmp_path: Path) -> None:
    fixture = tmp_path / "synthetic-vault"
    shutil.copytree(ROOT, fixture)
    card_path = fixture / "cards" / "card-agent-memory.json"
    card = json.loads(card_path.read_text(encoding="utf-8"))
    card.pop("last_reviewed")
    card.pop("review_interval_days")
    card_path.write_text(json.dumps(card), encoding="utf-8")

    code = main([
        "score",
        "--root",
        str(fixture),
        "--as-of",
        "2026-06-11",
    ])
    assert code == 1


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
