"""HTML scraper using httpx + BeautifulSoup.

Used as a fallback for sources that don't expose an RSS feed.
Attempts to extract article links and titles from the page.
"""
from __future__ import annotations

import logging
import re
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.scrapers import ArticleDraft

logger = logging.getLogger(__name__)

_TIMEOUT = 20
_MAX_LINKS = 15
_HEADERS = {"User-Agent": "AI-Pulse/0.1 (news aggregator)"}


def fetch(source: dict) -> list[ArticleDraft]:
    """Scrape article links from a webpage via BeautifulSoup."""
    url: str = source.get("url", "")
    if not url:
        return []

    try:
        resp = httpx.get(url, headers=_HEADERS, timeout=_TIMEOUT, follow_redirects=True)
        resp.raise_for_status()
        html = resp.text
    except Exception as exc:
        logger.warning("HTML scraper error for %s: %s", url, exc)
        return []

    soup = BeautifulSoup(html, "lxml")
    base_domain = urlparse(url).netloc

    seen_urls: set[str] = set()
    drafts: list[ArticleDraft] = []

    # Try <article> tags first, then fall back to prominent <a> tags
    candidates = soup.find_all("article") or []
    link_tags: list = []
    if candidates:
        for article in candidates[:_MAX_LINKS]:
            a = article.find("a", href=True)
            if a:
                link_tags.append(a)
    else:
        # Heuristic: look for links inside headings
        for tag in soup.find_all(["h1", "h2", "h3"]):
            a = tag.find("a", href=True)
            if a:
                link_tags.append(a)

    # Also grab all links from the page as a final fallback
    if not link_tags:
        link_tags = soup.find_all("a", href=True)

    for a in link_tags[:_MAX_LINKS * 3]:
        href = a.get("href", "").strip()
        if not href or href.startswith("#") or href.startswith("javascript:"):
            continue
        full_url = urljoin(url, href)
        if urlparse(full_url).netloc != base_domain:
            continue  # stay on-domain
        if full_url in seen_urls:
            continue
        # Skip obvious non-article URLs
        if re.search(r"/(tag|category|author|page|login|signup|about|contact)/", full_url):
            continue
        seen_urls.add(full_url)

        title = a.get_text(strip=True) or full_url
        if len(title) < 10:
            continue  # too short to be a real title

        drafts.append(
            ArticleDraft(
                source_id=source["id"],
                url=full_url,
                title=title[:250],
                raw_excerpt="",
            )
        )
        if len(drafts) >= _MAX_LINKS:
            break

    logger.info("HTML scraper %s → %d links", source.get("id"), len(drafts))
    return drafts
