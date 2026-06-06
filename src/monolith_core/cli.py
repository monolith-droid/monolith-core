from __future__ import annotations

import argparse
import json
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
        "root": str(root),
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
