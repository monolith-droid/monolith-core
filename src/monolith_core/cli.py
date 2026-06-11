from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

from .model import (
    ValidationError,
    load_branch_return,
    load_cards,
    load_context_pack,
    load_growth_idea_queue,
    load_index,
)


def _print_json(value: dict[str, Any]) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def _public_path(path: Path) -> str:
    return str(path).replace("\\", "/")


def _score_item(
    score_id: str,
    title: str,
    score: float,
    threshold: float,
    source_refs: list[str],
    evidence: dict[str, Any],
    next_action: str,
) -> dict[str, Any]:
    rounded = round(max(0.0, min(100.0, score)), 2)
    return {
        "score_id": score_id,
        "title": title,
        "score": rounded,
        "threshold": threshold,
        "status": "pass" if rounded >= threshold else "needs_growth",
        "source_refs": source_refs,
        "evidence": evidence,
        "next_action": next_action,
    }


def validate_root(root: Path) -> dict[str, Any]:
    cards = load_cards(root)
    index = load_index(root / "index.json")
    context_pack = load_context_pack(root / "context-pack.json")
    branch_return = load_branch_return(root / "branch-return.json")

    card_ids = {card.card_id for card in cards}
    index_ids = {entry["card_id"] for entry in index["entries"]}
    pack_ids = set(context_pack["card_ids"])
    branch_card_refs = set(branch_return["card_refs"])

    blockers: list[str] = []
    missing_from_index = sorted(card_ids - index_ids)
    unknown_index_cards = sorted(index_ids - card_ids)
    unknown_pack_cards = sorted(pack_ids - card_ids)
    unknown_branch_cards = sorted(branch_card_refs - card_ids)

    if missing_from_index:
        blockers.append("cards_missing_from_index:" + ",".join(missing_from_index))
    if unknown_index_cards:
        blockers.append("index_refs_unknown_cards:" + ",".join(unknown_index_cards))
    if unknown_pack_cards:
        blockers.append("context_pack_refs_unknown_cards:" + ",".join(unknown_pack_cards))
    if unknown_branch_cards:
        blockers.append("branch_return_refs_unknown_cards:" + ",".join(unknown_branch_cards))

    return {
        "passed": not blockers,
        "status": "valid" if not blockers else "invalid",
        "root": _public_path(root),
        "card_count": len(cards),
        "index_entry_count": len(index["entries"]),
        "context_pack_card_count": len(context_pack["card_ids"]),
        "branch_return_finding_count": len(branch_return["findings"]),
        "blockers": blockers,
    }


def run_validate(args: argparse.Namespace) -> int:
    result = validate_root(Path(args.root))
    _print_json(result)
    return 0 if result["passed"] else 1


def run_pack(args: argparse.Namespace) -> int:
    index = load_index(Path(args.index))
    context_pack = load_context_pack(Path(args.pack))
    index_ids = {entry["card_id"] for entry in index["entries"]}
    pack_ids = set(context_pack["card_ids"])
    blockers = []
    unknown = sorted(pack_ids - index_ids)
    if unknown:
        blockers.append("context_pack_refs_unknown_index_cards:" + ",".join(unknown))
    _print_json(
        {
            "passed": not blockers,
            "status": "context_pack_valid" if not blockers else "context_pack_invalid",
            "pack_id": context_pack["pack_id"],
            "card_count": len(context_pack["card_ids"]),
            "blockers": blockers,
        }
    )
    return 0 if not blockers else 1


def context_pack_diff_report(base_path: Path, candidate_path: Path) -> dict[str, Any]:
    base = load_context_pack(base_path)
    candidate = load_context_pack(candidate_path)
    base_ids = set(base["card_ids"])
    candidate_ids = set(candidate["card_ids"])
    added = sorted(candidate_ids - base_ids)
    removed = sorted(base_ids - candidate_ids)
    unchanged = sorted(base_ids & candidate_ids)
    changed = bool(added or removed)
    return {
        "diff_id": "diff-synthetic-context-pack",
        "passed": True,
        "status": "context_pack_changed" if changed else "context_pack_unchanged",
        "mode": "report_only",
        "mutation_performed": False,
        "base_pack": {
            "path": _public_path(base_path),
            "pack_id": base["pack_id"],
            "card_count": len(base["card_ids"]),
        },
        "candidate_pack": {
            "path": _public_path(candidate_path),
            "pack_id": candidate["pack_id"],
            "card_count": len(candidate["card_ids"]),
        },
        "added_card_ids": added,
        "removed_card_ids": removed,
        "unchanged_card_ids": unchanged,
        "added_count": len(added),
        "removed_count": len(removed),
        "unchanged_count": len(unchanged),
        "blockers": [],
        "warnings": [],
    }


def run_context_pack_diff(args: argparse.Namespace) -> int:
    report = context_pack_diff_report(Path(args.base), Path(args.candidate))
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _print_json(report)
    return 0


def run_branch_return_check(args: argparse.Namespace) -> int:
    report = load_branch_return(Path(args.report))
    blockers = []
    if not report["source_index_refs"]:
        blockers.append("source_index_refs_required")
    if not report["card_refs"]:
        blockers.append("card_refs_required")
    _print_json(
        {
            "passed": not blockers,
            "status": "branch_return_valid" if not blockers else "branch_return_invalid",
            "branch_id": report["branch_id"],
            "finding_count": len(report["findings"]),
            "blockers": blockers,
        }
    )
    return 0 if not blockers else 1


def score_root(root: Path, as_of: date | None = None) -> dict[str, Any]:
    as_of = as_of or date.today()
    validation = validate_root(root)
    cards = load_cards(root)
    index = load_index(root / "index.json")
    context_pack = load_context_pack(root / "context-pack.json")
    branch_return = load_branch_return(root / "branch-return.json")

    card_ids = {card.card_id for card in cards}
    index_ids = {entry["card_id"] for entry in index["entries"]}
    pack_ids = set(context_pack["card_ids"])
    branch_card_refs = set(branch_return["card_refs"])

    indexed_known_count = len(card_ids & index_ids)
    packed_known_count = len(card_ids & pack_ids)
    branch_known_count = len(card_ids & branch_card_refs)
    provenance_count = len([card for card in cards if card.source_refs])
    freshness_metadata_cards = [
        card for card in cards if card.last_reviewed is not None and card.review_interval_days is not None
    ]
    stale_cards = []
    for card in freshness_metadata_cards:
        assert card.last_reviewed is not None
        assert card.review_interval_days is not None
        age_days = (as_of - card.last_reviewed).days
        if age_days > card.review_interval_days:
            stale_cards.append(
                {
                    "card_id": card.card_id,
                    "age_days": age_days,
                    "review_interval_days": card.review_interval_days,
                }
            )

    card_count = len(cards)
    scores = [
        _score_item(
            "score-index-coverage",
            "Index Coverage",
            (indexed_known_count / card_count) * 100,
            100,
            ["index.json", "cards/*.json"],
            {"indexed_known_card_count": indexed_known_count, "card_count": card_count},
            "Add every public-safe card to the knowledge index.",
        ),
        _score_item(
            "score-context-pack-completeness",
            "Context Pack Completeness",
            (packed_known_count / card_count) * 100,
            90,
            ["context-pack.json", "cards/*.json"],
            {"packed_known_card_count": packed_known_count, "card_count": card_count},
            "Refresh the context pack so the agent can recover the full task context.",
        ),
        _score_item(
            "score-provenance-coverage",
            "Provenance Coverage",
            (provenance_count / card_count) * 100,
            100,
            ["cards/*.json"],
            {"cards_with_source_refs": provenance_count, "card_count": card_count},
            "Add synthetic source references before promoting a card to shared memory.",
        ),
        _score_item(
            "score-branch-return-coverage",
            "Branch Return Coverage",
            (branch_known_count / card_count) * 100,
            90,
            ["branch-return.json", "cards/*.json"],
            {"branch_return_known_card_count": branch_known_count, "card_count": card_count},
            "Link branch findings back to the core card set.",
        ),
        _score_item(
            "score-stale-card-detection",
            "Stale Card Detection",
            (len(freshness_metadata_cards) / card_count) * 100,
            100,
            ["cards/*.json"],
            {
                "cards_with_freshness_metadata": len(freshness_metadata_cards),
                "card_count": card_count,
                "as_of": as_of.isoformat(),
                "stale_cards": stale_cards,
            },
            "Add last_reviewed and review_interval_days to every card.",
        ),
    ]
    low_scores = [score for score in scores if score["status"] != "pass"]
    blockers = list(validation["blockers"])
    warnings = [f"stale_cards_detected:{','.join(item['card_id'] for item in stale_cards)}"] if stale_cards else []
    overall_score = round(sum(score["score"] for score in scores) / len(scores), 2)
    return {
        "scorecard_id": "scorecard-synthetic-core",
        "passed": not low_scores and not blockers,
        "status": "scorecard_ready" if not low_scores and not blockers else "scorecard_needs_growth",
        "mode": "report_only",
        "mutation_performed": False,
        "root": _public_path(root),
        "as_of": as_of.isoformat(),
        "overall_score": overall_score,
        "score_count": len(scores),
        "low_score_count": len(low_scores),
        "scores": scores,
        "blockers": blockers,
        "warnings": warnings,
    }


def run_score(args: argparse.Namespace) -> int:
    try:
        as_of = date.fromisoformat(args.as_of) if args.as_of else None
    except ValueError:
        _print_json({"passed": False, "status": "validation_error", "blockers": ["as_of_must_use_yyyy_mm_dd"]})
        return 1
    report = score_root(Path(args.root), as_of=as_of)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _print_json(report)
    return 0 if report["passed"] else 1


def _idea_priority(idea: dict[str, Any]) -> float:
    raw = (idea["impact"] * idea["confidence"]) / idea["effort"]
    return round(min(100.0, raw * 4), 2)


def growth_queue_report(queue_path: Path, limit: int = 3) -> dict[str, Any]:
    queue = load_growth_idea_queue(queue_path)
    ideas = queue["ideas"]
    candidates = [idea for idea in ideas if idea["status"] == "candidate"]
    blockers = [] if candidates else ["growth_queue_requires_candidate_ideas"]
    ranked = sorted(
        candidates,
        key=lambda idea: (-_idea_priority(idea), -idea["impact"], idea["effort"], idea["idea_id"]),
    )
    top_ideas = [
        {
            "idea_id": idea["idea_id"],
            "title": idea["title"],
            "priority_score": _idea_priority(idea),
            "impact": idea["impact"],
            "effort": idea["effort"],
            "confidence": idea["confidence"],
            "public_safety": idea["public_safety"],
            "source_refs": idea["source_refs"],
            "next_action": idea["next_action"],
        }
        for idea in ranked[:limit]
    ]
    return {
        "queue_id": queue["queue_id"],
        "passed": not blockers,
        "status": "growth_queue_ready" if not blockers else "growth_queue_blocked",
        "mode": "report_only",
        "mutation_performed": False,
        "queue": _public_path(queue_path),
        "generated_at": queue["generated_at"],
        "source_refs": queue["source_refs"],
        "idea_count": len(ideas),
        "candidate_count": len(candidates),
        "selected_count": len(top_ideas),
        "top_ideas": top_ideas,
        "blockers": blockers,
        "warnings": [],
    }


def run_growth_queue(args: argparse.Namespace) -> int:
    if args.limit < 1:
        _print_json({"passed": False, "status": "validation_error", "blockers": ["limit_must_be_positive"]})
        return 1
    report = growth_queue_report(Path(args.queue), limit=args.limit)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _print_json(report)
    return 0 if report["passed"] else 1


def _repair_step(
    step_id: str,
    title: str,
    severity: str,
    source_refs: list[str],
    evidence: dict[str, Any],
    recommended_action: str,
) -> dict[str, Any]:
    return {
        "repair_step_id": step_id,
        "title": title,
        "severity": severity,
        "source_refs": source_refs,
        "evidence": evidence,
        "recommended_action": recommended_action,
    }


def _steps_from_validation_blockers(blockers: list[str]) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    for blocker in blockers:
        key, _, raw_detail = blocker.partition(":")
        details = [part for part in raw_detail.split(",") if part]
        if key == "cards_missing_from_index":
            steps.append(
                _repair_step(
                    "repair-step-add-cards-to-index",
                    "Add missing cards to the knowledge index",
                    "high",
                    ["index.json", "cards/*.json"],
                    {"missing_card_ids": details},
                    "Add each public-safe card id to index.json with a relative synthetic path and tags.",
                )
            )
        elif key == "index_refs_unknown_cards":
            steps.append(
                _repair_step(
                    "repair-step-remove-unknown-index-refs",
                    "Remove or create unknown index card references",
                    "high",
                    ["index.json", "cards/*.json"],
                    {"unknown_card_ids": details},
                    "Either add synthetic card fixtures for these ids or remove the stale index entries.",
                )
            )
        elif key == "context_pack_refs_unknown_cards":
            steps.append(
                _repair_step(
                    "repair-step-refresh-context-pack",
                    "Refresh context-pack card references",
                    "high",
                    ["context-pack.json", "cards/*.json"],
                    {"unknown_card_ids": details},
                    "Update the context pack so every referenced card id exists in the public fixture.",
                )
            )
        elif key == "branch_return_refs_unknown_cards":
            steps.append(
                _repair_step(
                    "repair-step-refresh-branch-return-refs",
                    "Refresh branch-return card references",
                    "medium",
                    ["branch-return.json", "cards/*.json"],
                    {"unknown_card_ids": details},
                    "Link branch-return findings back to known public-safe cards.",
                )
            )
        else:
            steps.append(
                _repair_step(
                    "repair-step-review-validation-blocker",
                    "Review validation blocker",
                    "high",
                    ["synthetic fixture"],
                    {"blocker": blocker},
                    "Convert the validation blocker into a public-safe fixture or schema update.",
                )
            )
    return steps


def _steps_from_score_report(report: dict[str, Any]) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    steps.extend(_steps_from_validation_blockers(list(report["blockers"])))
    for score in report["scores"]:
        if score["status"] == "pass":
            continue
        steps.append(
            _repair_step(
                "repair-step-" + score["score_id"].removeprefix("score-"),
                "Improve " + score["title"],
                "medium",
                list(score["source_refs"]),
                {
                    "score_id": score["score_id"],
                    "score": score["score"],
                    "threshold": score["threshold"],
                    "evidence": score["evidence"],
                },
                score["next_action"],
            )
        )
    for warning in report["warnings"]:
        if warning.startswith("stale_cards_detected:"):
            card_ids = [part for part in warning.partition(":")[2].split(",") if part]
            steps.append(
                _repair_step(
                    "repair-step-review-stale-cards",
                    "Review stale cards",
                    "low",
                    ["cards/*.json"],
                    {"stale_card_ids": card_ids},
                    "Review stale public-safe cards and update last_reviewed only after human-visible review.",
                )
            )
        else:
            steps.append(
                _repair_step(
                    "repair-step-review-score-warning",
                    "Review score warning",
                    "low",
                    ["scorecard"],
                    {"warning": warning},
                    "Turn the warning into a public-safe schema, fixture, or documentation improvement.",
                )
            )
    return steps


def repair_plan_report(root: Path, as_of: date | None = None) -> dict[str, Any]:
    as_of = as_of or date.today()
    try:
        source_report = score_root(root, as_of=as_of)
        source_status = source_report["status"]
        source_passed = source_report["passed"]
        steps = _steps_from_score_report(source_report)
        source_refs = ["scorecard-synthetic-core", "examples/synthetic-vault/scorecard.json"]
    except ValidationError as exc:
        source_status = "validation_error"
        source_passed = False
        steps = [
            _repair_step(
                "repair-step-fix-fixture-shape",
                "Fix fixture shape",
                "high",
                ["synthetic fixture"],
                {"error": str(exc)},
                "Fix the public fixture so MONOLITH Core can load it before scoring repairs.",
            )
        ]
        source_refs = ["validation_error"]

    return {
        "repair_plan_id": "repair-plan-synthetic-core",
        "passed": True,
        "status": "repair_plan_ready" if steps else "repair_not_needed",
        "mode": "report_only",
        "mutation_performed": False,
        "root": _public_path(root),
        "as_of": as_of.isoformat(),
        "source_status": source_status,
        "source_passed": source_passed,
        "source_refs": source_refs,
        "repair_step_count": len(steps),
        "repair_steps": steps,
        "blockers": [],
        "warnings": [],
    }


def run_repair_plan(args: argparse.Namespace) -> int:
    try:
        as_of = date.fromisoformat(args.as_of) if args.as_of else None
    except ValueError:
        _print_json({"passed": False, "status": "validation_error", "blockers": ["as_of_must_use_yyyy_mm_dd"]})
        return 1
    report = repair_plan_report(Path(args.root), as_of=as_of)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _print_json(report)
    return 0


def _parse_synthetic_note(path: Path) -> tuple[dict[str, str | list[str]], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        raise ValidationError(f"{path}: synthetic note must start with frontmatter")
    try:
        end = lines[1:].index("---") + 1
    except ValueError as exc:
        raise ValidationError(f"{path}: synthetic note frontmatter must end with ---") from exc

    fields: dict[str, str | list[str]] = {}
    current_list_key: str | None = None
    for line in lines[1:end]:
        if line.startswith("  - "):
            if current_list_key is None:
                raise ValidationError(f"{path}: list item without key")
            value = line[4:].strip()
            if not value:
                raise ValidationError(f"{path}: list values must be non-empty")
            existing = fields.setdefault(current_list_key, [])
            if not isinstance(existing, list):
                raise ValidationError(f"{path}: {current_list_key} mixes scalar and list values")
            existing.append(value)
            continue
        if ":" not in line:
            raise ValidationError(f"{path}: frontmatter lines must use key: value")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if not key:
            raise ValidationError(f"{path}: frontmatter keys must be non-empty")
        if raw_value:
            fields[key] = raw_value
            current_list_key = None
        else:
            fields[key] = []
            current_list_key = key

    body = "\n".join(lines[end + 1 :]).strip()
    if not body:
        raise ValidationError(f"{path}: synthetic note body must be non-empty")
    return fields, body


def _required_note_string(fields: dict[str, str | list[str]], key: str, path: Path) -> str:
    value = fields.get(key)
    if not isinstance(value, str) or not value:
        raise ValidationError(f"{path}: {key} must be a non-empty frontmatter string")
    return value


def _required_note_list(fields: dict[str, str | list[str]], key: str, path: Path) -> list[str]:
    value = fields.get(key)
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        raise ValidationError(f"{path}: {key} must be a non-empty frontmatter list")
    return value


def _note_summary(body: str) -> str:
    paragraphs = [part.strip() for part in body.split("\n\n") if part.strip()]
    for paragraph in paragraphs:
        if paragraph.startswith("#"):
            continue
        return " ".join(paragraph.split())
    raise ValidationError("synthetic note body must include a summary paragraph")


def adapter_example_report(note_path: Path) -> dict[str, Any]:
    fields, body = _parse_synthetic_note(note_path)
    card_id = _required_note_string(fields, "card_id", note_path)
    title = _required_note_string(fields, "title", note_path)
    tags = _required_note_list(fields, "tags", note_path)
    source_refs = _required_note_list(fields, "source_refs", note_path)
    index_id = _required_note_string(fields, "index_id", note_path)
    pack_id = _required_note_string(fields, "pack_id", note_path)
    purpose = _required_note_string(fields, "purpose", note_path)
    output_path = _required_note_string(fields, "output_path", note_path)
    last_reviewed = _required_note_string(fields, "last_reviewed", note_path)
    try:
        review_interval_days = int(_required_note_string(fields, "review_interval_days", note_path))
    except ValueError as exc:
        raise ValidationError(f"{note_path}: review_interval_days must be an integer") from exc
    if review_interval_days <= 0:
        raise ValidationError(f"{note_path}: review_interval_days must be positive")

    card = {
        "card_id": card_id,
        "title": title,
        "summary": _note_summary(body),
        "tags": tags,
        "source_refs": source_refs,
        "last_reviewed": last_reviewed,
        "review_interval_days": review_interval_days,
    }
    index = {
        "index_id": index_id,
        "entries": [
            {
                "card_id": card_id,
                "path": output_path,
                "tags": tags,
            }
        ],
    }
    context_pack = {
        "pack_id": pack_id,
        "purpose": purpose,
        "card_ids": [card_id],
    }
    return {
        "adapter_example_id": "adapter-example-synthetic-note",
        "passed": True,
        "status": "adapter_example_ready",
        "mode": "report_only",
        "mutation_performed": False,
        "note": _public_path(note_path),
        "contract_count": 3,
        "contracts": {
            "card": card,
            "index": index,
            "context_pack": context_pack,
        },
        "blockers": [],
        "warnings": [],
    }


def run_adapter_example(args: argparse.Namespace) -> int:
    report = adapter_example_report(Path(args.note))
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _print_json(report)
    return 0


def run_curate_dry_run(args: argparse.Namespace) -> int:
    result = validate_root(Path(args.root))
    report = {
        "passed": result["passed"],
        "status": "curation_ready_report_only" if result["passed"] else "curation_blocked",
        "mode": "dry_run",
        "mutation_performed": False,
        "root": result["root"],
        "card_count": result["card_count"],
        "proposed_actions": [
            "refresh_context_pack",
            "review_branch_return_findings",
            "flag_stale_cards_for_human_review",
        ]
        if result["passed"]
        else [],
        "blockers": result["blockers"],
    }
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _print_json(report)
    return 0 if report["passed"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="monolith-core")
    subcommands = parser.add_subparsers(dest="command", required=True)

    validate = subcommands.add_parser("validate", help="Validate a synthetic MONOLITH Core vault fixture.")
    validate.add_argument("--root", required=True)
    validate.set_defaults(func=run_validate)

    pack = subcommands.add_parser("pack", help="Validate that a context pack references indexed cards.")
    pack.add_argument("--index", required=True)
    pack.add_argument("--pack", required=True)
    pack.set_defaults(func=run_pack)

    diff = subcommands.add_parser("context-pack-diff", help="Compare two public context-pack fixtures report-only.")
    diff.add_argument("--base", required=True)
    diff.add_argument("--candidate", required=True)
    diff.add_argument("--out")
    diff.set_defaults(func=run_context_pack_diff)

    branch = subcommands.add_parser("branch-return-check", help="Validate a branch-return report.")
    branch.add_argument("--report", required=True)
    branch.set_defaults(func=run_branch_return_check)

    score = subcommands.add_parser("score", help="Render a public-safe memory health scorecard.")
    score.add_argument("--root", required=True)
    score.add_argument("--as-of", help="Evaluate freshness as of YYYY-MM-DD.")
    score.add_argument("--out")
    score.set_defaults(func=run_score)

    growth = subcommands.add_parser("growth-queue", help="Rank a public-safe self-growth idea queue.")
    growth.add_argument("--queue", required=True)
    growth.add_argument("--limit", type=int, default=3)
    growth.add_argument("--out")
    growth.set_defaults(func=run_growth_queue)

    repair = subcommands.add_parser("repair-plan", help="Render a report-only repair plan from validation or score results.")
    repair.add_argument("--root", required=True)
    repair.add_argument("--as-of", help="Evaluate freshness as of YYYY-MM-DD.")
    repair.add_argument("--out")
    repair.set_defaults(func=run_repair_plan)

    adapter = subcommands.add_parser(
        "adapter-example",
        help="Convert a synthetic Markdown-like note into public JSON contract examples.",
    )
    adapter.add_argument("--note", required=True)
    adapter.add_argument("--out")
    adapter.set_defaults(func=run_adapter_example)

    curate = subcommands.add_parser("curate-dry-run", help="Render a report-only curator plan.")
    curate.add_argument("--root", required=True)
    curate.add_argument("--out")
    curate.set_defaults(func=run_curate_dry_run)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ValidationError as exc:
        _print_json({"passed": False, "status": "validation_error", "blockers": [str(exc)]})
        return 1
