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

    branch = subcommands.add_parser("branch-return-check", help="Validate a branch-return report.")
    branch.add_argument("--report", required=True)
    branch.set_defaults(func=run_branch_return_check)

    score = subcommands.add_parser("score", help="Render a public-safe memory health scorecard.")
    score.add_argument("--root", required=True)
    score.add_argument("--as-of", help="Evaluate freshness as of YYYY-MM-DD.")
    score.add_argument("--out")
    score.set_defaults(func=run_score)

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
