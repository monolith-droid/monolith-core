from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


ID_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
ID_PREFIXES = {
    "card_id": "card-",
    "index_id": "index-",
    "pack_id": "pack-",
    "branch_id": "branch-",
    "finding_id": "finding-",
    "scorecard_id": "scorecard-",
    "score_id": "score-",
}


class ValidationError(ValueError):
    """Raised when a public MONOLITH Core fixture is invalid."""


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValidationError(f"{path} must contain a JSON object")
    return value


def require_string(value: dict[str, Any], key: str, path: Path) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item.strip():
        raise ValidationError(f"{path}: {key} must be a non-empty string")
    return item


def require_id(value: dict[str, Any], key: str, path: Path) -> str:
    item = require_string(value, key, path)
    prefix = ID_PREFIXES[key]
    if not item.startswith(prefix):
        raise ValidationError(f"{path}: {key} must start with {prefix}")
    if not ID_PATTERN.fullmatch(item):
        raise ValidationError(f"{path}: {key} must use lowercase words, digits, and hyphens")
    return item


def require_id_list(value: dict[str, Any], key: str, prefix_key: str, path: Path) -> list[str]:
    items = require_string_list(value, key, path)
    prefix = ID_PREFIXES[prefix_key]
    for item in items:
        if not item.startswith(prefix):
            raise ValidationError(f"{path}: {key} entries must start with {prefix}")
        if not ID_PATTERN.fullmatch(item):
            raise ValidationError(f"{path}: {key} entries must use lowercase words, digits, and hyphens")
    return items


def require_string_list(value: dict[str, Any], key: str, path: Path) -> list[str]:
    item = value.get(key)
    if not isinstance(item, list) or not all(isinstance(part, str) and part.strip() for part in item):
        raise ValidationError(f"{path}: {key} must be a list of non-empty strings")
    return item


def optional_date(value: dict[str, Any], key: str, path: Path) -> date | None:
    item = value.get(key)
    if item is None:
        return None
    if not isinstance(item, str) or not item.strip():
        raise ValidationError(f"{path}: {key} must be an ISO date string")
    try:
        return date.fromisoformat(item)
    except ValueError as exc:
        raise ValidationError(f"{path}: {key} must use YYYY-MM-DD") from exc


def optional_positive_int(value: dict[str, Any], key: str, path: Path) -> int | None:
    item = value.get(key)
    if item is None:
        return None
    if not isinstance(item, int) or item <= 0:
        raise ValidationError(f"{path}: {key} must be a positive integer")
    return item


@dataclass(frozen=True)
class KnowledgeCard:
    card_id: str
    title: str
    summary: str
    tags: list[str]
    source_refs: list[str]
    last_reviewed: date | None
    review_interval_days: int | None
    path: Path


def load_card(path: Path) -> KnowledgeCard:
    value = read_json(path)
    return KnowledgeCard(
        card_id=require_id(value, "card_id", path),
        title=require_string(value, "title", path),
        summary=require_string(value, "summary", path),
        tags=require_string_list(value, "tags", path),
        source_refs=require_string_list(value, "source_refs", path),
        last_reviewed=optional_date(value, "last_reviewed", path),
        review_interval_days=optional_positive_int(value, "review_interval_days", path),
        path=path,
    )


def load_cards(root: Path) -> list[KnowledgeCard]:
    cards_dir = root / "cards"
    if not cards_dir.is_dir():
        raise ValidationError(f"{cards_dir} is missing")
    cards = [load_card(path) for path in sorted(cards_dir.glob("*.json"))]
    if not cards:
        raise ValidationError(f"{cards_dir} must contain at least one card")
    ids = [card.card_id for card in cards]
    duplicate_ids = sorted({card_id for card_id in ids if ids.count(card_id) > 1})
    if duplicate_ids:
        raise ValidationError(f"duplicate card ids: {', '.join(duplicate_ids)}")
    return cards


def load_index(path: Path) -> dict[str, Any]:
    value = read_json(path)
    require_id(value, "index_id", path)
    entries = value.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValidationError(f"{path}: entries must be a non-empty list")
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValidationError(f"{path}: entries[{index}] must be an object")
        require_id(entry, "card_id", path)
        require_string(entry, "path", path)
        require_string_list(entry, "tags", path)
    return value


def load_context_pack(path: Path) -> dict[str, Any]:
    value = read_json(path)
    require_id(value, "pack_id", path)
    require_string(value, "purpose", path)
    require_id_list(value, "card_ids", "card_id", path)
    return value


def load_branch_return(path: Path) -> dict[str, Any]:
    value = read_json(path)
    require_id(value, "branch_id", path)
    require_id_list(value, "source_index_refs", "index_id", path)
    require_id_list(value, "card_refs", "card_id", path)
    findings = value.get("findings")
    if not isinstance(findings, list) or not findings:
        raise ValidationError(f"{path}: findings must be a non-empty list")
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            raise ValidationError(f"{path}: findings[{index}] must be an object")
        require_id(finding, "finding_id", path)
        require_string(finding, "status", path)
        require_string(finding, "summary", path)
    return value
