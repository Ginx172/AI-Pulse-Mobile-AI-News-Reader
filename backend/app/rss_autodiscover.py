"""RSS feed auto-discovery helper.

Tries common feed paths on a given URL and parses the HTML <head> for
<link rel="alternate" type="application/rss+xml"> elements.
"""
from __future__ import annotations

import ipaddress
import logging
import socket
from urllib.parse import urljoin, urlparse

import feedparser
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_COMMON_PATHS = [
    "/feed",
    "/rss",
    "/feed.xml",
    "/rss.xml",
    "/atom.xml",
    "/feed/",
    "/rss/",
]

_ALLOWED_SCHEMES = {"http", "https"}


def _is_safe_url(url: str) -> bool:
    """Return False if the URL targets a private/loopback/reserved address or has a disallowed scheme.

    If DNS resolution fails (e.g., host unreachable or not found), we allow the URL optimistically —
    the downstream HTTP call will simply fail in that case.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in _ALLOWED_SCHEMES:
            return False
        hostname = parsed.hostname
        if not hostname:
            return False
        # Resolve hostname to IP(s) and check none are private/reserved
        try:
            infos = socket.getaddrinfo(hostname, None)
        except socket.gaierror:
            # Host cannot be resolved right now; allow optimistically
            return True
        for info in infos:
            addr = info[4][0]
            try:
                ip = ipaddress.ip_address(addr)
                if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local:
                    return False
            except ValueError:
                pass
        return True
    except Exception:  # noqa: BLE001
        return False


async def autodiscover_rss(url: str, client: httpx.AsyncClient) -> str | None:
    """Return a working RSS/Atom feed URL for *url*, or None if not found.

    Strategy:
    1. Try common feed path suffixes.
    2. Fetch the HTML <head> and look for <link rel="alternate" type="application/rss+xml">.
    """
    if not _is_safe_url(url):
        logger.debug("autodiscover: URL failed safety check, skipping: %s", url)
        return None

    base = _base_url(url)

    # Step 1: common paths
    for path in _COMMON_PATHS:
        candidate = urljoin(base, path)
        if _is_valid_feed(candidate):
            logger.debug("autodiscover: found feed at %s", candidate)
            return candidate

    # Step 2: HTML head discovery
    try:
        resp = await client.get(url, timeout=10, follow_redirects=True)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            for link in soup.find_all("link", rel="alternate"):
                link_type = link.get("type", "")
                if "rss" in link_type or "atom" in link_type:
                    href = link.get("href")
                    if href:
                        candidate = urljoin(url, href)
                        if _is_safe_url(candidate) and _is_valid_feed(candidate):
                            logger.debug("autodiscover: found feed via HTML head at %s", candidate)
                            return candidate
    except Exception as exc:  # noqa: BLE001
        logger.debug("autodiscover: HTML fetch failed for %s: %s", url, exc)

    return None


def _base_url(url: str) -> str:
    """Return scheme + netloc of a URL."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def _is_valid_feed(url: str) -> bool:
    """Return True if feedparser can successfully parse the URL."""
    try:
        d = feedparser.parse(url)
        return not d.bozo and len(d.entries) > 0
    except Exception:  # noqa: BLE001
        return False
