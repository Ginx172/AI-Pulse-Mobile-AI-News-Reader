"""Sources loader — merges official catalog, custom YAML, custom DB, and overrides.

Merge order (later wins on duplicate id):
  1. Official YAML  (top_100_ai_sources.yaml)
  2. Custom YAML    (custom_sources.yaml)
  3. Custom DB      (custom_sources table)

Active flag is determined by:
  - source.active field (custom sources)
  - SourceOverride.active  (for official + custom sources, if an override row exists)

Effective weight = source.weight * (override.weight_override or 1.0)
"""
from __future__ import annotations

import logging
from typing import Any

import yaml

from app.config import settings

logger = logging.getLogger(__name__)


def load_official_sources() -> list[dict[str, Any]]:
    """Load sources from the official top_100_ai_sources.yaml catalog."""
    try:
        with open(settings.sources_yaml, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except FileNotFoundError:
        logger.warning("Official sources YAML not found at %s", settings.sources_yaml)
        return []
    sources = data.get("sources", []) or []
    # Official sources are always active unless overridden
    for src in sources:
        src.setdefault("active", True)
    return sources


def load_custom_sources_from_yaml() -> list[dict[str, Any]]:
    """Load user-added sources from custom_sources.yaml."""
    try:
        with open(settings.custom_sources_yaml, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except FileNotFoundError:
        return []
    if not data:
        return []
    sources = data.get("sources", []) or []
    for src in sources:
        src.setdefault("active", True)
        src.setdefault("weight", 1.2)
        src.setdefault("category", "custom")
        src.setdefault("type", "blog")
        src.setdefault("language", "en")
    return sources


def load_custom_sources_from_db() -> list[dict[str, Any]]:
    """Load user-added sources from the custom_sources DB table."""
    try:
        from app.db import SessionLocal
        from app.models import CustomSource

        db = SessionLocal()
        try:
            rows = db.query(CustomSource).all()
            return [
                {
                    "id": r.id,
                    "name": r.name,
                    "url": r.url,
                    "rss_url": r.rss_url,
                    "category": r.category or "custom",
                    "type": r.type or "blog",
                    "language": r.language or "en",
                    "weight": r.weight if r.weight is not None else 1.2,
                    "active": r.active if r.active is not None else True,
                }
                for r in rows
            ]
        finally:
            db.close()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not load custom sources from DB: %s", exc)
        return []


def _get_overrides() -> dict[str, dict[str, Any]]:
    """Return {source_id: {active, weight_override}} from the source_overrides table."""
    try:
        from app.db import SessionLocal
        from app.models import SourceOverride

        db = SessionLocal()
        try:
            rows = db.query(SourceOverride).all()
            return {
                r.source_id: {
                    "active": r.active if r.active is not None else True,
                    "weight_override": r.weight_override,
                }
                for r in rows
            }
        finally:
            db.close()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not load source overrides from DB: %s", exc)
        return {}


def load_all_sources() -> list[dict[str, Any]]:
    """Merge all source lists, apply overrides, and filter out inactive sources.

    Dedup by ``id``; later sources win (DB > custom YAML > official YAML).
    Returns only sources where effective_active is True.
    """
    merged: dict[str, dict[str, Any]] = {}

    for src in load_official_sources():
        merged[src["id"]] = src

    for src in load_custom_sources_from_yaml():
        merged[src["id"]] = src

    for src in load_custom_sources_from_db():
        merged[src["id"]] = src

    overrides = _get_overrides()

    result: list[dict[str, Any]] = []
    for src in merged.values():
        src_id = src["id"]
        override = overrides.get(src_id, {})

        effective_active = override.get("active", src.get("active", True))
        if not effective_active:
            continue

        weight_override = override.get("weight_override")
        base_weight = src.get("weight", 1.0)
        effective_weight = base_weight * weight_override if weight_override else base_weight

        enriched = dict(src)
        enriched["effective_active"] = effective_active
        enriched["effective_weight"] = effective_weight
        result.append(enriched)

    return result
