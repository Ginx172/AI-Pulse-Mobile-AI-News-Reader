"""Minimal backend test suite.

Tests:
  1. GET /health returns 200 with {"status": "ok"}
  2. Ranking function deterministically picks ≤ 25 from a mock set of 60
  3. Extractive summariser works offline (no API keys)
"""
from __future__ import annotations

import datetime
import os
import sys
import tempfile

import pytest

# Ensure we can import from the backend package regardless of CWD
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ─── Override DB to a temp file-based SQLite for tests ────────────────────────
_tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp_db.close()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_db.name}"
os.environ.setdefault("ANTHROPIC_API_KEY", "")
os.environ.setdefault("GEMINI_API_KEY", "")
os.environ.setdefault("GROQ_API_KEY", "")
os.environ.setdefault("OPENAI_API_KEY", "")
os.environ.setdefault("MISTRAL_API_KEY", "")
os.environ.setdefault("TOGETHER_API_KEY", "")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.ranking import rank_and_select  # noqa: E402
from app.scrapers import ArticleDraft  # noqa: E402
from app.summarizer import _summarise_extractive, summarise  # noqa: E402


@pytest.fixture(scope="session")
def client():
    """Session-scoped TestClient; startup event runs on first request."""
    with TestClient(app) as c:
        yield c


# ─── Test 1: /health ──────────────────────────────────────────────────────────


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ─── Test 2: /sources returns non-empty list ──────────────────────────────────


def test_sources(client):
    response = client.get("/sources")
    assert response.status_code == 200
    sources = response.json()
    assert isinstance(sources, list)
    assert len(sources) == 103, f"Expected 103 sources, got {len(sources)}"


# ─── Test 3: /articles/today returns list ─────────────────────────────────────


def test_articles_today(client):
    response = client.get("/articles/today")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ─── Test 4: Ranking picks ≤ 25 from 60 mock articles ────────────────────────


def _make_drafts(n: int) -> list[ArticleDraft]:
    base = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    drafts = []
    for i in range(n):
        drafts.append(
            ArticleDraft(
                source_id=f"source-{i % 10}",
                url=f"https://example.com/article-{i}",
                title=f"Article {i} about AI model release benchmark",
                published_at=base - datetime.timedelta(hours=i * 2),
                raw_excerpt=f"Some text about article {i}. Points: {i * 5}",
            )
        )
    return drafts


def test_ranking_picks_25_from_60():
    drafts = _make_drafts(60)
    source_weights = {f"source-{i}": 1.0 for i in range(10)}
    top = rank_and_select(drafts, source_weights, top_n=25)
    assert len(top) == 25, f"Expected 25 articles, got {len(top)}"


def test_ranking_deterministic():
    drafts = _make_drafts(60)
    source_weights = {f"source-{i}": 1.0 for i in range(10)}
    top1 = rank_and_select(drafts, source_weights, top_n=25)
    top2 = rank_and_select(drafts, source_weights, top_n=25)
    urls1 = [d.url for d, _ in top1]
    urls2 = [d.url for d, _ in top2]
    assert urls1 == urls2, "Ranking is not deterministic"


def test_ranking_sorted_descending():
    drafts = _make_drafts(60)
    source_weights = {f"source-{i}": 1.0 for i in range(10)}
    top = rank_and_select(drafts, source_weights, top_n=25)
    scores = [s for _, s in top]
    assert scores == sorted(scores, reverse=True), "Results not sorted by score descending"


def test_ranking_fewer_than_top_n():
    """When fewer than top_n articles exist, return all of them."""
    drafts = _make_drafts(10)
    source_weights = {f"source-{i}": 1.0 for i in range(10)}
    top = rank_and_select(drafts, source_weights, top_n=25)
    assert len(top) == 10


# ─── Test 5: Extractive summariser (offline) ──────────────────────────────────


def test_extractive_three_sentences():
    text = (
        "Researchers at MIT have unveiled a new AI model. "
        "The model achieves state-of-the-art results on multiple benchmarks. "
        "It is open-sourced under the MIT licence. "
        "This fourth sentence should not appear."
    )
    result = _summarise_extractive(text, title="New MIT Model")
    sentences = [s.strip() for s in result.split(". ") if s.strip()]
    # Should contain at most 3 sentences
    assert len(sentences) <= 3
    assert "Researchers at MIT" in result


def test_extractive_empty_text():
    result = _summarise_extractive("", title="Empty")
    assert isinstance(result, str)
    assert len(result) >= 0  # should not crash


def test_extractive_short_text():
    text = "Short text."
    result = _summarise_extractive(text, title="Short")
    assert "Short text" in result


# ─── Test 6: summarise() falls through to extractive with no keys ─────────────


def test_summarise_falls_back_to_extractive_without_keys(monkeypatch):
    """When all provider API keys are empty, summarise() uses extractive fallback."""
    monkeypatch.setattr("app.summarizer.settings.groq_api_key", "")
    monkeypatch.setattr("app.summarizer.settings.anthropic_api_key", "")
    monkeypatch.setattr("app.summarizer.settings.openai_api_key", "")
    monkeypatch.setattr("app.summarizer.settings.mistral_api_key", "")
    monkeypatch.setattr("app.summarizer.settings.together_api_key", "")
    monkeypatch.setattr("app.summarizer.settings.gemini_api_key", "")

    text = (
        "Researchers at DeepMind have published a new paper on reinforcement learning. "
        "The paper shows significant improvements over previous baselines. "
        "The code is available on GitHub under an open-source licence. "
        "This fourth sentence should not appear."
    )
    result = summarise(text, title="DeepMind RL Paper")
    # Should return extractive summary (first 3 sentences, no API calls)
    assert isinstance(result, str)
    assert len(result) > 0
    assert "Researchers at DeepMind" in result

