"""Reddit JSON scraper (public API, no auth required).

Uses the Reddit public JSON endpoint as a fallback when the RSS feed is not
suitable or to obtain engagement metrics.
"""
from __future__ import annotations

import datetime
import logging
from typing import Optional

import httpx

from app.scrapers import ArticleDraft

logger = logging.getLogger(__name__)

_REDDIT_JSON = "https://www.reddit.com/r/{subreddit}/hot.json?limit=20"
_HEADERS = {"User-Agent": "AI-Pulse/0.1 (news aggregator)"}
_TIMEOUT = 15


def _subreddit_from_source(source: dict) -> Optional[str]:
    url: str = source.get("url", "")
    # e.g. https://www.reddit.com/r/MachineLearning/
    parts = url.rstrip("/").split("/")
    try:
        idx = parts.index("r")
        return parts[idx + 1]
    except (ValueError, IndexError):
        return None


def fetch(source: dict) -> list[ArticleDraft]:
    """Fetch hot posts from a subreddit via the public JSON endpoint."""
    subreddit = _subreddit_from_source(source)
    if not subreddit:
        logger.warning("Cannot determine subreddit from source %s", source.get("id"))
        return []

    url = _REDDIT_JSON.format(subreddit=subreddit)
    try:
        resp = httpx.get(url, headers=_HEADERS, timeout=_TIMEOUT, follow_redirects=True)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        logger.warning("Reddit JSON error for %s: %s", subreddit, exc)
        return []

    drafts: list[ArticleDraft] = []
    for child in data.get("data", {}).get("children", []):
        post = child.get("data", {})
        link = post.get("url", "").strip()
        if not link or link.startswith("https://www.reddit.com/r/") and "/comments/" not in link:
            # skip self-posts that don't have an external URL
            permalink = "https://www.reddit.com" + post.get("permalink", "")
            link = permalink

        title = post.get("title", "No title").strip()
        author = post.get("author", None)
        created = post.get("created_utc")
        published_at: Optional[datetime.datetime] = None
        if created:
            try:
                published_at = datetime.datetime.utcfromtimestamp(float(created))
            except Exception:
                pass

        selftext = post.get("selftext", "") or ""
        raw_excerpt = selftext[:500]

        drafts.append(
            ArticleDraft(
                source_id=source["id"],
                url=link,
                title=title,
                author=author,
                published_at=published_at,
                raw_excerpt=raw_excerpt,
            )
        )

    logger.info("Reddit JSON %s → %d posts", subreddit, len(drafts))
    return drafts
