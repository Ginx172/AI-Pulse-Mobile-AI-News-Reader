"""Hacker News scraper via the Algolia search API.

Fetches recent HN stories that mention AI-related keywords.
"""
from __future__ import annotations

import datetime
import logging
from typing import Optional

import httpx

from app.scrapers import ArticleDraft

logger = logging.getLogger(__name__)

_HN_ALGOLIA = (
    "https://hn.algolia.com/api/v1/search"
    "?tags=story"
    "&query=AI+OR+LLM+OR+machine+learning"
    "&hitsPerPage=30"
    "&numericFilters=points>10"
)
_TIMEOUT = 15


def fetch(source: dict) -> list[ArticleDraft]:
    """Fetch AI-related stories from Hacker News via the Algolia API."""
    try:
        resp = httpx.get(_HN_ALGOLIA, timeout=_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        logger.warning("HN Algolia error: %s", exc)
        return []

    drafts: list[ArticleDraft] = []
    for hit in data.get("hits", []):
        url = hit.get("url", "").strip()
        if not url:
            # Fallback to HN discussion page
            object_id = hit.get("objectID", "")
            if not object_id:
                continue
            url = f"https://news.ycombinator.com/item?id={object_id}"

        title = hit.get("title", "No title").strip()
        author = hit.get("author", None)

        created_str = hit.get("created_at", "")
        published_at: Optional[datetime.datetime] = None
        if created_str:
            try:
                published_at = datetime.datetime.fromisoformat(created_str.replace("Z", "+00:00"))
            except Exception:
                pass

        raw_excerpt = f"Points: {hit.get('points', 0)} | Comments: {hit.get('num_comments', 0)}"

        drafts.append(
            ArticleDraft(
                source_id=source["id"],
                url=url,
                title=title,
                author=author,
                published_at=published_at,
                raw_excerpt=raw_excerpt,
            )
        )

    logger.info("HN Algolia → %d stories", len(drafts))
    return drafts
