"""Tests for custom source CRUD and autodiscovery."""
from __future__ import annotations

import os
import sys
import tempfile
from unittest.mock import AsyncMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

_tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp_db.close()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_db.name}"
os.environ.setdefault("ANTHROPIC_API_KEY", "")
os.environ.setdefault("GEMINI_API_KEY", "")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.sources_loader import load_custom_sources_from_yaml  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


# ─── POST /sources/custom ─────────────────────────────────────────────────────

def test_create_custom_source_with_rss_autodiscovery(client):
    """POST without rss_url — autodiscovery (mocked) returns a feed."""
    discovered_url = "https://simonwillison.net/atom/everything/"

    with patch("app.main.autodiscover_rss", new=AsyncMock(return_value=discovered_url)):
        resp = client.post(
            "/sources/custom",
            json={"name": "Simon Willison", "url": "https://simonwillison.net"},
        )

    assert resp.status_code == 201
    data = resp.json()
    assert data["rss_url"] == discovered_url
    assert data["id"] == "simon-willison"
    assert data["active"] is True


def test_create_custom_source_explicit_rss(client):
    """POST with explicit rss_url skips autodiscovery."""
    resp = client.post(
        "/sources/custom",
        json={
            "name": "Test Blog",
            "url": "https://testblog.example.com",
            "rss_url": "https://testblog.example.com/feed.xml",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["rss_url"] == "https://testblog.example.com/feed.xml"


def test_create_custom_source_invalid_url(client):
    """POST with invalid URL should return 400."""
    resp = client.post(
        "/sources/custom",
        json={"name": "Bad Source", "url": "not-a-url"},
    )
    assert resp.status_code == 400


def test_duplicate_id_gets_suffix(client):
    """Creating two sources with same name should produce id-2, id-3 etc."""
    with patch("app.main.autodiscover_rss", new=AsyncMock(return_value=None)):
        r1 = client.post("/sources/custom", json={"name": "Dup Source", "url": "https://a.example.com"})
        r2 = client.post("/sources/custom", json={"name": "Dup Source", "url": "https://b.example.com"})
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["id"] != r2.json()["id"]
    assert r2.json()["id"] == "dup-source-2"


# ─── GET /sources/custom ──────────────────────────────────────────────────────

def test_list_custom_sources(client):
    resp = client.get("/sources/custom")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


# ─── PATCH /sources/custom/{id} ──────────────────────────────────────────────

def test_patch_custom_source_active(client):
    """PATCH toggles active; source should then be excluded from load_all_sources if False."""
    # Create a source
    with patch("app.main.autodiscover_rss", new=AsyncMock(return_value=None)):
        resp = client.post(
            "/sources/custom",
            json={"name": "Toggle Blog", "url": "https://toggle.example.com"},
        )
    assert resp.status_code == 201
    src_id = resp.json()["id"]

    # Disable it
    patch_resp = client.patch(f"/sources/custom/{src_id}", json={"active": False})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["active"] is False

    # Confirm excluded from load_all_sources
    from app.sources_loader import load_all_sources
    sources = load_all_sources()
    ids = [s["id"] for s in sources]
    assert src_id not in ids


# ─── DELETE /sources/custom/{id} ─────────────────────────────────────────────

def test_delete_custom_source(client):
    """DELETE removes source from DB."""
    with patch("app.main.autodiscover_rss", new=AsyncMock(return_value=None)):
        resp = client.post(
            "/sources/custom",
            json={"name": "To Delete", "url": "https://delete-me.example.com"},
        )
    assert resp.status_code == 201
    src_id = resp.json()["id"]

    del_resp = client.delete(f"/sources/custom/{src_id}")
    assert del_resp.status_code == 204

    # Confirm gone
    list_resp = client.get("/sources/custom")
    ids = [s["id"] for s in list_resp.json()]
    assert src_id not in ids


def test_delete_nonexistent_returns_404(client):
    resp = client.delete("/sources/custom/does-not-exist-xyz")
    assert resp.status_code == 404


# ─── YAML custom source loader ────────────────────────────────────────────────

def test_load_custom_sources_from_yaml_empty(tmp_path, monkeypatch):
    """Empty custom_sources.yaml returns empty list."""
    yaml_path = tmp_path / "custom_sources.yaml"
    yaml_path.write_text("sources: []\n")

    from app import config as cfg
    monkeypatch.setattr(cfg.settings, "custom_sources_yaml", str(yaml_path))

    result = load_custom_sources_from_yaml()
    assert result == []


def test_load_custom_sources_from_yaml_with_entry(tmp_path, monkeypatch):
    """YAML with one entry is loaded and merged correctly."""
    yaml_content = """sources:
  - id: yaml-custom-blog
    name: "YAML Custom Blog"
    url: "https://yamlcustom.example.com"
    rss_url: "https://yamlcustom.example.com/feed.xml"
    category: custom
    type: blog
    language: en
    weight: 1.2
    active: true
"""
    yaml_path = tmp_path / "custom_sources.yaml"
    yaml_path.write_text(yaml_content)

    from app import config as cfg
    monkeypatch.setattr(cfg.settings, "custom_sources_yaml", str(yaml_path))

    result = load_custom_sources_from_yaml()
    assert len(result) == 1
    assert result[0]["id"] == "yaml-custom-blog"
    assert result[0]["active"] is True
