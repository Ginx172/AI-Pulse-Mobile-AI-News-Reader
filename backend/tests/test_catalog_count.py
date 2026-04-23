"""Test that the official source catalog contains exactly 103 entries."""
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("ANTHROPIC_API_KEY", "")
os.environ.setdefault("GEMINI_API_KEY", "")

from app.sources_loader import load_official_sources  # noqa: E402


def test_official_source_count():
    sources = load_official_sources()
    assert len(sources) == 103, f"Expected 103 official sources, got {len(sources)}"


def test_official_sources_have_required_fields():
    sources = load_official_sources()
    required = {"id", "name", "url", "category", "type"}
    for src in sources:
        missing = required - src.keys()
        assert not missing, f"Source {src.get('id')} is missing fields: {missing}"


def test_no_duplicate_ids():
    sources = load_official_sources()
    ids = [s["id"] for s in sources]
    assert len(ids) == len(set(ids)), "Duplicate source IDs found in official catalog"
