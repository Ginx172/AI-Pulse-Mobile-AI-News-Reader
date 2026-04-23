"""Article ranking algorithm.

Score = w1*recency + w2*source_weight + w3*keyword_relevance + w4*engagement

Default weights: w1=0.4, w2=0.3, w3=0.2, w4=0.1
"""
from __future__ import annotations

import datetime
import math
import re
from typing import Optional

from app.scrapers import ArticleDraft

# Default weights
W1_RECENCY = 0.4
W2_SOURCE_WEIGHT = 0.3
W3_KEYWORD = 0.2
W4_ENGAGEMENT = 0.1

TOP_N = 25

KEYWORDS = [
    "release",
    "open source",
    "benchmark",
    "tutorial",
    "how to",
    "guide",
    "launch",
    "paper",
    "model",
    "agent",
]


def _recency_score(published_at: Optional[datetime.datetime]) -> float:
    """Return a 0–1 recency score. Articles older than 7 days score 0."""
    if published_at is None:
        return 0.3  # unknown date — give a modest score
    now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    # Normalise tz-aware datetimes
    if published_at.tzinfo is not None:
        published_at = published_at.replace(tzinfo=None)
    age_hours = max(0.0, (now - published_at).total_seconds() / 3600)
    # Decay over 7 days (168 hours)
    return max(0.0, 1.0 - age_hours / 168.0)


def _keyword_score(text: str) -> float:
    """Return a 0–1 score based on how many keywords appear in the text."""
    lower = text.lower()
    hits = sum(1 for kw in KEYWORDS if kw in lower)
    return min(1.0, hits / 3.0)  # 3 hits = full score


def _engagement_score(raw_excerpt: str) -> float:
    """Parse engagement hints (e.g. 'Points: 42') from the raw excerpt."""
    match = re.search(r"points?[:\s]+(\d+)", raw_excerpt, re.IGNORECASE)
    if match:
        points = int(match.group(1))
        # Log-scale normalised against 1000 points
        return min(1.0, math.log1p(points) / math.log1p(1000))
    return 0.0


def score_article(
    draft: ArticleDraft,
    source_weight: float = 1.0,
    w1: float = W1_RECENCY,
    w2: float = W2_SOURCE_WEIGHT,
    w3: float = W3_KEYWORD,
    w4: float = W4_ENGAGEMENT,
) -> float:
    """Compute a composite score for a single article draft."""
    recency = _recency_score(draft.published_at)
    keyword = _keyword_score(draft.title + " " + draft.raw_excerpt)
    engagement = _engagement_score(draft.raw_excerpt)

    return (
        w1 * recency
        + w2 * source_weight
        + w3 * keyword
        + w4 * engagement
    )


def rank_and_select(
    drafts: list[ArticleDraft],
    source_weights: dict[str, float],
    top_n: int = TOP_N,
) -> list[tuple[ArticleDraft, float]]:
    """Score all drafts, sort descending, and return the top *top_n* with scores.

    Args:
        drafts: All deduplicated article drafts.
        source_weights: Mapping of source_id → weight.
        top_n: Number of articles to select.

    Returns:
        List of (draft, score) tuples, highest score first, length ≤ top_n.
    """
    scored = [
        (draft, score_article(draft, source_weight=source_weights.get(draft.source_id, 1.0)))
        for draft in drafts
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_n]
