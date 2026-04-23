"""Daily pipeline: load sources → scrape → dedupe → rank → summarise → persist."""
from __future__ import annotations

import datetime
import logging

from app.db import SessionLocal, create_tables
from app.models import Article, Source
from app.ranking import rank_and_select
from app.scrapers import ArticleDraft
from app.scrapers import rss as rss_scraper
from app.scrapers import hn as hn_scraper
from app.scrapers import reddit as reddit_scraper
from app.sources_loader import load_all_sources
from app.summarizer import summarise

logger = logging.getLogger(__name__)


def _scrape_source(source: dict) -> list[ArticleDraft]:
    """Dispatch to the appropriate scraper based on source type."""
    src_type: str = source.get("type", "")
    src_id: str = source.get("id", "")

    if src_id == "hacker-news-ai":
        return hn_scraper.fetch(source)

    if src_type == "reddit":
        # Try RSS first, fall back to JSON
        drafts = rss_scraper.fetch(source)
        if not drafts:
            drafts = reddit_scraper.fetch(source)
        return drafts

    # Default: use RSS for anything that has an rss_url
    if source.get("rss_url"):
        return rss_scraper.fetch(source)

    return []


def _dedupe(drafts: list[ArticleDraft]) -> list[ArticleDraft]:
    """Remove duplicate articles by URL."""
    seen: set[str] = set()
    unique: list[ArticleDraft] = []
    for draft in drafts:
        if draft.url not in seen:
            seen.add(draft.url)
            unique.append(draft)
    return unique


def run_daily() -> None:
    """Execute the full daily pipeline and persist results."""
    logger.info("Daily pipeline starting …")
    create_tables()

    sources = load_all_sources()
    # Use effective_weight (respects weight_override) for ranking
    source_weights = {s["id"]: s.get("effective_weight", s.get("weight", 1.0)) for s in sources}

    # 1. Scrape all active sources (inactive already filtered by load_all_sources)
    all_drafts: list[ArticleDraft] = []
    for source in sources:
        try:
            drafts = _scrape_source(source)
            all_drafts.extend(drafts)
        except Exception as exc:
            logger.warning("Scraper error for %s: %s", source.get("id"), exc)

    logger.info("Total raw articles fetched: %d", len(all_drafts))

    # 2. Deduplicate
    unique_drafts = _dedupe(all_drafts)
    logger.info("After deduplication: %d unique articles", len(unique_drafts))

    # 3. Rank and select top 25
    top_articles = rank_and_select(unique_drafts, source_weights)
    logger.info("Top %d articles selected", len(top_articles))

    today = datetime.date.today()

    # 4. Summarise and persist
    db = SessionLocal()
    try:
        # Mark previous selections for today as unselected
        db.query(Article).filter(
            Article.day == today, Article.selected_for_today
        ).update({"selected_for_today": False})
        db.commit()

        # Ensure sources are in DB
        for source in sources:
            if not db.query(Source).filter(Source.id == source["id"]).first():
                db.add(
                    Source(
                        id=source["id"],
                        name=source["name"],
                        url=source["url"],
                        rss_url=source.get("rss_url"),
                        category=source["category"],
                        type=source["type"],
                        language=source.get("language", "en"),
                        weight=source.get("weight", 1.0),
                    )
                )
        db.commit()

        for draft, score in top_articles:
            # Upsert by URL
            existing = db.query(Article).filter(Article.url == draft.url).first()
            excerpt = draft.raw_excerpt or ""
            summary_text = summarise(excerpt, title=draft.title)

            if existing:
                existing.score = score
                existing.selected_for_today = True
                existing.day = today
                existing.summary = summary_text
            else:
                db.add(
                    Article(
                        source_id=draft.source_id,
                        url=draft.url,
                        title=draft.title,
                        author=draft.author,
                        published_at=draft.published_at,
                        raw_excerpt=excerpt,
                        summary=summary_text,
                        score=score,
                        selected_for_today=True,
                        day=today,
                    )
                )

        db.commit()
        logger.info("Pipeline complete — %d articles saved for %s", len(top_articles), today)
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_daily()
