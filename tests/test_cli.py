from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path

from jsonschema import Draft202012Validator

from monolith_core.cli import (
    adapter_example_report,
    adapter_readiness_report,
    context_pack_diff_report,
    growth_queue_report,
    main,
    release_readiness_report,
    repair_plan_report,
    score_root,
    validate_root,
    validation_summary_report,
)


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


def test_validation_summary_fixture_matches_report_command() -> None:
    fixture = json.loads((ROOT / "validation-summary.json").read_text(encoding="utf-8"))
    result = validation_summary_report(ROOT)
    assert result == fixture


def test_validation_summary_command_passes() -> None:
    code = main([
        "validation-summary",
        "--root",
        "examples/synthetic-vault",
    ])
    assert code == 0


def test_validation_summary_handles_validation_errors(tmp_path: Path) -> None:
    fixture = tmp_path / "synthetic-vault"
    shutil.copytree(ROOT, fixture)
    card_path = fixture / "cards" / "card-agent-memory.json"
    card = json.loads(card_path.read_text(encoding="utf-8"))
    card["card_id"] = "Card_AgentMemory"
    card_path.write_text(json.dumps(card), encoding="utf-8")

    result = validation_summary_report(fixture)

    assert result["passed"] is True
    assert result["source_passed"] is False
    assert result["source_status"] == "validation_error"
    assert result["blocker_count"] == 1
    assert result["next_actions"] == ["fix_public_fixture_shape_before_validation"]


def test_growth_queue_report_ranks_candidate_ideas() -> None:
    report = growth_queue_report(ROOT / "growth-ideas.json")

    assert report["passed"] is True
    assert report["status"] == "growth_queue_ready"
    assert report["mode"] == "report_only"
    assert report["mutation_performed"] is False
    assert report["idea_count"] == 9
    assert report["candidate_count"] == 1
    assert report["selected_count"] == 1
    assert report["top_ideas"][0]["idea_id"] == "idea-stable-contract-migration-guide"
    assert report["top_ideas"][0]["priority_score"] == 26.67
    assert report["blockers"] == []
    assert report["warnings"] == []


def test_growth_queue_command_passes() -> None:
    code = main([
        "growth-queue",
        "--queue",
        "examples/synthetic-vault/growth-ideas.json",
    ])
    assert code == 0


def test_growth_queue_rejects_private_adapter_only_ideas(tmp_path: Path) -> None:
    queue = tmp_path / "growth-ideas.json"
    value = json.loads((ROOT / "growth-ideas.json").read_text(encoding="utf-8"))
    value["ideas"][0]["public_safety"] = "private_adapter_only"
    queue.write_text(json.dumps(value), encoding="utf-8")

    code = main([
        "growth-queue",
        "--queue",
        str(queue),
    ])
    assert code == 1


def test_repair_plan_fixture_matches_report_command() -> None:
    fixture = json.loads((ROOT / "repair-plan.json").read_text(encoding="utf-8"))
    result = repair_plan_report(ROOT, as_of=date(2026, 7, 15))
    assert result == fixture


def test_repair_plan_command_passes() -> None:
    code = main([
        "repair-plan",
        "--root",
        "examples/synthetic-vault",
        "--as-of",
        "2026-07-15",
    ])
    assert code == 0


def test_repair_plan_handles_missing_freshness_metadata(tmp_path: Path) -> None:
    fixture = tmp_path / "synthetic-vault"
    shutil.copytree(ROOT, fixture)
    card_path = fixture / "cards" / "card-agent-memory.json"
    card = json.loads(card_path.read_text(encoding="utf-8"))
    card.pop("last_reviewed")
    card.pop("review_interval_days")
    card_path.write_text(json.dumps(card), encoding="utf-8")

    result = repair_plan_report(fixture, as_of=date(2026, 6, 11))

    assert result["passed"] is True
    assert result["source_passed"] is False
    assert result["status"] == "repair_plan_ready"
    assert result["repair_steps"][0]["repair_step_id"] == "repair-step-stale-card-detection"


def test_repair_plan_handles_validation_errors(tmp_path: Path) -> None:
    fixture = tmp_path / "synthetic-vault"
    shutil.copytree(ROOT, fixture)
    card_path = fixture / "cards" / "card-agent-memory.json"
    card = json.loads(card_path.read_text(encoding="utf-8"))
    card["card_id"] = "Card_AgentMemory"
    card_path.write_text(json.dumps(card), encoding="utf-8")

    result = repair_plan_report(fixture, as_of=date(2026, 6, 11))

    assert result["passed"] is True
    assert result["source_passed"] is False
    assert result["source_status"] == "validation_error"
    assert result["repair_steps"][0]["repair_step_id"] == "repair-step-fix-fixture-shape"


def test_adapter_example_fixture_matches_report_command() -> None:
    fixture = json.loads((ROOT / "adapter-example.json").read_text(encoding="utf-8"))
    result = adapter_example_report(ROOT / "adapter-note.md")
    assert result == fixture


def test_adapter_example_command_passes() -> None:
    code = main([
        "adapter-example",
        "--note",
        "examples/synthetic-vault/adapter-note.md",
    ])
    assert code == 0


def test_adapter_example_rejects_missing_frontmatter(tmp_path: Path) -> None:
    note = tmp_path / "bad-note.md"
    note.write_text("# Bad Note\n\nNo frontmatter here.\n", encoding="utf-8")

    code = main([
        "adapter-example",
        "--note",
        str(note),
    ])
    assert code == 1


def test_adapter_readiness_fixture_matches_report_command() -> None:
    fixture = json.loads((ROOT / "adapter-readiness-report.json").read_text(encoding="utf-8"))
    result = adapter_readiness_report(ROOT / "adapter-readiness.json")
    assert result == fixture


def test_adapter_readiness_profile_and_report_match_schemas() -> None:
    profile = json.loads((ROOT / "adapter-readiness.json").read_text(encoding="utf-8"))
    report = json.loads((ROOT / "adapter-readiness-report.json").read_text(encoding="utf-8"))
    profile_schema = json.loads(Path("schemas/adapter-readiness-profile.schema.json").read_text(encoding="utf-8"))
    report_schema = json.loads(Path("schemas/adapter-readiness-report.schema.json").read_text(encoding="utf-8"))

    Draft202012Validator.check_schema(profile_schema)
    Draft202012Validator(profile_schema).validate(profile)
    Draft202012Validator.check_schema(report_schema)
    Draft202012Validator(report_schema).validate(report)


def test_adapter_readiness_command_passes() -> None:
    code = main([
        "adapter-readiness",
        "--adapter",
        "examples/synthetic-vault/adapter-readiness.json",
    ])
    assert code == 0


def test_adapter_readiness_rejects_private_reference_without_echoing_it(tmp_path: Path, capsys) -> None:
    profile = json.loads((ROOT / "adapter-readiness.json").read_text(encoding="utf-8"))
    private_value = "../private-note.md"
    profile["lanes"][0]["public_refs"] = [private_value]
    path = tmp_path / "adapter.json"
    path.write_text(json.dumps(profile), encoding="utf-8")

    code = main(["adapter-readiness", "--adapter", str(path)])
    output = capsys.readouterr().out
    result = json.loads(output)

    assert code == 1
    assert result["status"] == "adapter_readiness_blocked"
    assert "private_reference_detected" in result["blockers"]
    assert private_value not in output


def test_adapter_readiness_rejects_private_authority(tmp_path: Path) -> None:
    profile = json.loads((ROOT / "adapter-readiness.json").read_text(encoding="utf-8"))
    profile["lanes"][1]["authority"]["scheduler"] = True
    path = tmp_path / "adapter.json"
    path.write_text(json.dumps(profile), encoding="utf-8")

    result = adapter_readiness_report(path)

    assert result["passed"] is False
    assert "private_adapter_authority_not_allowed" in result["blockers"]
    assert result["warnings"] == []


def test_blocked_adapter_readiness_fixture_fails_closed_without_private_value(capsys) -> None:
    code = main([
        "adapter-readiness",
        "--adapter",
        "examples/synthetic-vault/adapter-readiness-blocked.json",
    ])
    output = capsys.readouterr().out
    result = json.loads(output)

    assert code == 1
    assert result["status"] == "adapter_readiness_blocked"
    assert "private_reference_detected" in result["blockers"]
    assert "private_adapter_authority_not_allowed" in result["blockers"]
    assert "../private-note.md" not in output


def test_pack_command_passes() -> None:
    code = main([
        "pack",
        "--index",
        "examples/synthetic-vault/index.json",
        "--pack",
        "examples/synthetic-vault/context-pack.json",
    ])
    assert code == 0


def test_context_pack_diff_fixture_matches_report_command() -> None:
    fixture = json.loads((ROOT / "context-pack-diff.json").read_text(encoding="utf-8"))
    result = context_pack_diff_report(ROOT / "context-pack.json", ROOT / "context-pack-expanded.json")
    assert result == fixture


def test_context_pack_diff_command_passes() -> None:
    code = main([
        "context-pack-diff",
        "--base",
        "examples/synthetic-vault/context-pack.json",
        "--candidate",
        "examples/synthetic-vault/context-pack-expanded.json",
    ])
    assert code == 0


def test_context_pack_diff_detects_removed_cards(tmp_path: Path) -> None:
    candidate = tmp_path / "context-pack-small.json"
    value = json.loads((ROOT / "context-pack.json").read_text(encoding="utf-8"))
    value["card_ids"] = ["card-agent-memory"]
    candidate.write_text(json.dumps(value), encoding="utf-8")

    result = context_pack_diff_report(ROOT / "context-pack.json", candidate)

    assert result["status"] == "context_pack_changed"
    assert result["added_card_ids"] == []
    assert result["removed_card_ids"] == ["card-branch-return"]
    assert result["unchanged_card_ids"] == ["card-agent-memory"]


def test_release_readiness_fixture_matches_report_command() -> None:
    fixture = json.loads((ROOT / "release-readiness.json").read_text(encoding="utf-8"))
    result = release_readiness_report(
        ROOT,
        ROOT / "growth-ideas.json",
        ROOT / "context-pack.json",
        ROOT / "context-pack-expanded.json",
        as_of=date(2026, 6, 12),
    )
    assert result == fixture


def test_release_readiness_command_passes() -> None:
    code = main([
        "release-readiness",
        "--root",
        "examples/synthetic-vault",
        "--queue",
        "examples/synthetic-vault/growth-ideas.json",
        "--base-pack",
        "examples/synthetic-vault/context-pack.json",
        "--candidate-pack",
        "examples/synthetic-vault/context-pack-expanded.json",
        "--as-of",
        "2026-06-12",
    ])
    assert code == 0


def test_release_readiness_blocks_on_validation_errors(tmp_path: Path) -> None:
    fixture = tmp_path / "synthetic-vault"
    shutil.copytree(ROOT, fixture)
    card_path = fixture / "cards" / "card-agent-memory.json"
    card = json.loads(card_path.read_text(encoding="utf-8"))
    card["card_id"] = "Card_AgentMemory"
    card_path.write_text(json.dumps(card), encoding="utf-8")

    result = release_readiness_report(
        fixture,
        fixture / "growth-ideas.json",
        fixture / "context-pack.json",
        fixture / "context-pack-expanded.json",
        as_of=date(2026, 6, 12),
    )

    assert result["passed"] is False
    assert result["status"] == "release_blocked"
    assert result["passed_check_count"] == 2
    assert result["blockers"][0].startswith("readiness-check-validation-summary:")


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
