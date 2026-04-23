"""FastAPI application entry point."""
from __future__ import annotations

import datetime
import logging
from contextlib import asynccontextmanager
from typing import Any, Optional

import yaml
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.db import create_tables, get_db
from app.models import Article, Source
from app.scheduler import start_scheduler

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    create_tables()
    _seed_sources()
    start_scheduler()
    yield


app = FastAPI(title="AI Pulse", version="0.1.0", lifespan=lifespan)


# ─── Pydantic response schemas ────────────────────────────────────────────────

class SourceSchema(BaseModel):
    id: str
    name: str
    url: str
    rss_url: Optional[str]
    category: str
    type: str
    language: str
    weight: float

    model_config = {"from_attributes": True}


class ArticleSchema(BaseModel):
    id: int
    source_id: str
    url: str
    title: str
    author: Optional[str]
    published_at: Optional[datetime.datetime]
    summary: Optional[str]
    score: float
    selected_for_today: bool
    day: Optional[datetime.date]

    model_config = {"from_attributes": True}


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/sources", response_model=list[SourceSchema])
def list_sources(db: Session = Depends(get_db)) -> list[Source]:
    return db.query(Source).all()


@app.get("/articles/today", response_model=list[ArticleSchema])
def articles_today(db: Session = Depends(get_db)) -> list[Article]:
    today = datetime.date.today()
    return (
        db.query(Article)
        .filter(Article.day == today, Article.selected_for_today)  # noqa: E712
        .order_by(Article.score.desc())
        .limit(25)
        .all()
    )


@app.get("/articles/{article_id}", response_model=ArticleSchema)
def get_article(article_id: int, db: Session = Depends(get_db)) -> Article:
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


# ─── Seed sources from YAML ───────────────────────────────────────────────────

def _seed_sources() -> None:
    """Insert sources from YAML into DB (upsert by id)."""
    from app.db import SessionLocal

    try:
        with open(settings.sources_yaml, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except FileNotFoundError:
        logger.warning("sources YAML not found at %s — skipping seed", settings.sources_yaml)
        return

    db = SessionLocal()
    try:
        for entry in data.get("sources", []):
            existing = db.query(Source).filter(Source.id == entry["id"]).first()
            if not existing:
                db.add(
                    Source(
                        id=entry["id"],
                        name=entry["name"],
                        url=entry["url"],
                        rss_url=entry.get("rss_url"),
                        category=entry["category"],
                        type=entry["type"],
                        language=entry.get("language", "en"),
                        weight=entry.get("weight", 1.0),
                    )
                )
        db.commit()
    finally:
        db.close()
