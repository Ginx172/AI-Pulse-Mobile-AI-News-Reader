"""Tests for source overrides (enable/disable official sources, weight overrides)."""
from __future__ import annotations

import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

_tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp_db.close()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_db.name}"
os.environ.setdefault("ANTHROPIC_API_KEY", "")
os.environ.setdefault("GEMINI_API_KEY", "")

from fastapi.testclient import TestClient  # noqa: E402

from app.db import create_tables  # noqa: E402
from app.main import app  # noqa: E402
from app.sources_loader import load_all_sources  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_patch_source_disable(client):
    """PATCH /sources/{id} with active=false should disable the source."""
    # Disable openai-blog
    resp = client.patch("/sources/openai-blog", json={"active": False})
    assert resp.status_code == 200
    data = resp.json()
    assert data["active"] is False
    assert data["source_id"] == "openai-blog"


def test_disabled_source_excluded_from_load_all(client):
    """After disabling a source, load_all_sources should not include it."""
    # Ensure disabled (may already be from previous test)
    client.patch("/sources/openai-blog", json={"active": False})
    sources = load_all_sources()
    ids = [s["id"] for s in sources]
    assert "openai-blog" not in ids, "Disabled source should not appear in load_all_sources()"


def test_enable_source(client):
    """POST /sources/{id}/enable should re-enable a disabled source."""
    client.patch("/sources/openai-blog", json={"active": False})
    resp = client.post("/sources/openai-blog/enable")
    assert resp.status_code == 200
    assert resp.json()["active"] is True


def test_enabled_source_included_in_load_all(client):
    """After enabling a source, load_all_sources should include it again."""
    client.post("/sources/openai-blog/enable")
    sources = load_all_sources()
    ids = [s["id"] for s in sources]
    assert "openai-blog" in ids


def test_disable_convenience_endpoint(client):
    """POST /sources/{id}/disable convenience endpoint."""
    resp = client.post("/sources/huggingface-blog/disable")
    assert resp.status_code == 200
    assert resp.json()["active"] is False
    # Re-enable for cleanliness
    client.post("/sources/huggingface-blog/enable")


def test_weight_override_applied(client):
    """PATCH /sources/{id} with weight_override should affect effective_weight in GET /sources."""
    client.patch("/sources/huggingface-blog", json={"weight_override": 2.0})
    resp = client.get("/sources")
    assert resp.status_code == 200
    sources = resp.json()
    hf = next((s for s in sources if s["id"] == "huggingface-blog"), None)
    assert hf is not None
    assert hf["effective_weight"] == pytest.approx(hf["weight"] * 2.0)
    # Cleanup
    client.patch("/sources/huggingface-blog", json={"weight_override": None})


def test_get_sources_has_active_and_effective_weight(client):
    """GET /sources should include active and effective_weight fields."""
    resp = client.get("/sources")
    assert resp.status_code == 200
    sources = resp.json()
    assert len(sources) > 0
    for src in sources[:5]:
        assert "active" in src
        assert "effective_weight" in src
