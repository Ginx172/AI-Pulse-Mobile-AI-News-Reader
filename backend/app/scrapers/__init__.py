"""Shared data class used by all scrapers."""
from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ArticleDraft:
    source_id: str
    url: str
    title: str
    author: Optional[str] = None
    published_at: Optional[datetime.datetime] = None
    raw_excerpt: str = ""
