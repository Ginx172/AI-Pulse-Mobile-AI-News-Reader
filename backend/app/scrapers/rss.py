"""RSS/Atom scraper using feedparser.

Handles: blogs, Substack, YouTube RSS, podcast feeds, arXiv RSS, subreddit RSS.
"""
from __future__ import annotations

import datetime
import logging
from typing import Optional

import feedparser
from dateutil import parser as dateparser

from app.scrapers import ArticleDraft

logger = logging.getLogger(__name__)

_MAX_ENTRIES = 20  # per feed
_TIMEOUT = 15  # seconds


def fetch(source: dict) -> list[ArticleDraft]:
    """Fetch articles from an RSS/Atom feed.

    Args:
        source: A dict with at minimum ``id`` and ``rss_url`` keys.

    Returns:
        A list of :class:`ArticleDraft` objects (may be empty).
    """
    rss_url: Optional[str] = source.get("rss_url")
    if not rss_url:
        logger.debug("No rss_url for source %s — skipping RSS scraper", source.get("id"))
        return []

    try:
        feed = feedparser.parse(rss_url, request_headers={"User-Agent": "AI-Pulse/0.1"})
    except Exception as exc:
        logger.warning("feedparser error for %s: %s", rss_url, exc)
        return []

    drafts: list[ArticleDraft] = []
    for entry in feed.entries[:_MAX_ENTRIES]:
        url = entry.get("link", "").strip()
        if not url:
            continue

        title = entry.get("title", "No title").strip()
        author = entry.get("author", None)

        published_at: Optional[datetime.datetime] = None
        for attr in ("published_parsed", "updated_parsed"):
            val = entry.get(attr)
            if val:
                try:
                    published_at = datetime.datetime(*val[:6])
                except Exception:
                    pass
                break
        if published_at is None:
            for attr in ("published", "updated"):
                val = entry.get(attr, "")
                if val:
                    try:
                        published_at = dateparser.parse(val)
                    except Exception:
                        pass
                    break

        # Best-effort excerpt
        summary = entry.get("summary", "") or entry.get("description", "") or ""
        # Strip any embedded HTML tags crudely for the excerpt
        import re
        raw_excerpt = re.sub(r"<[^>]+>", " ", summary).strip()[:500]

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

    logger.info("RSS %s → %d entries", source.get("id"), len(drafts))
    return drafts
