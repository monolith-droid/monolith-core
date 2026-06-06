from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


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


def require_string_list(value: dict[str, Any], key: str, path: Path) -> list[str]:
    item = value.get(key)
    if not isinstance(item, list) or not all(isinstance(part, str) and part.strip() for part in item):
        raise ValidationError(f"{path}: {key} must be a list of non-empty strings")
    return item


@dataclass(frozen=True)
class KnowledgeCard:
    card_id: str
    title: str
    summary: str
    tags: list[str]
    source_refs: list[str]
    path: Path


def load_card(path: Path) -> KnowledgeCard:
    value = read_json(path)
    return KnowledgeCard(
        card_id=require_string(value, "card_id", path),
        title=require_string(value, "title", path),
        summary=require_string(value, "summary", path),
        tags=require_string_list(value, "tags", path),
        source_refs=require_string_list(value, "source_refs", path),
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
    require_string(value, "index_id", path)
    entries = value.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValidationError(f"{path}: entries must be a non-empty list")
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValidationError(f"{path}: entries[{index}] must be an object")
        require_string(entry, "card_id", path)
        require_string(entry, "path", path)
        require_string_list(entry, "tags", path)
    return value


def load_context_pack(path: Path) -> dict[str, Any]:
    value = read_json(path)
    require_string(value, "pack_id", path)
    require_string(value, "purpose", path)
    require_string_list(value, "card_ids", path)
    return value


def load_branch_return(path: Path) -> dict[str, Any]:
    value = read_json(path)
    require_string(value, "branch_id", path)
    require_string_list(value, "source_index_refs", path)
    require_string_list(value, "card_refs", path)
    findings = value.get("findings")
    if not isinstance(findings, list) or not findings:
        raise ValidationError(f"{path}: findings must be a non-empty list")
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            raise ValidationError(f"{path}: findings[{index}] must be an object")
        require_string(finding, "finding_id", path)
        require_string(finding, "status", path)
        require_string(finding, "summary", path)
    return value
