"""FastAPI application entry point."""
from __future__ import annotations

import datetime
import logging
import re
from contextlib import asynccontextmanager
from typing import Any, Optional

import httpx
import yaml
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.db import create_tables, get_db
from app.models import Article, CustomSource, Source, SourceOverride
from app.rss_autodiscover import _is_safe_url, autodiscover_rss
from app.scheduler import start_scheduler
from app.sources_loader import load_all_sources, load_official_sources

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
    active: bool = True
    effective_weight: float = 1.0

    model_config = {"from_attributes": True}


class CustomSourceSchema(BaseModel):
    id: str
    name: str
    url: str
    rss_url: Optional[str]
    category: str
    type: str
    language: str
    weight: float
    active: bool
    added_at: Optional[datetime.datetime]

    model_config = {"from_attributes": True}


class CustomSourceCreate(BaseModel):
    name: str
    url: str
    rss_url: Optional[str] = None
    category: Optional[str] = "custom"
    type: Optional[str] = "blog"
    weight: Optional[float] = 1.2


class CustomSourceUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    rss_url: Optional[str] = None
    weight: Optional[float] = None
    active: Optional[bool] = None


class SourceOverrideUpdate(BaseModel):
    active: Optional[bool] = None
    weight_override: Optional[float] = None


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
def list_sources(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    """Return all sources (official + custom) with active and effective_weight fields."""
    sources = load_all_sources()
    # Build override lookup
    overrides: dict[str, SourceOverride] = {
        o.source_id: o for o in db.query(SourceOverride).all()
    }
    result = []
    for src in sources:
        ovr = overrides.get(src["id"])
        active = ovr.active if ovr is not None and ovr.active is not None else src.get("active", True)
        base_weight = src.get("weight", 1.0)
        weight_override = ovr.weight_override if ovr else None
        effective_weight = base_weight * weight_override if weight_override else base_weight
        result.append(
            SourceSchema(
                id=src["id"],
                name=src["name"],
                url=src["url"],
                rss_url=src.get("rss_url"),
                category=src["category"],
                type=src["type"],
                language=src.get("language", "en"),
                weight=base_weight,
                active=active,
                effective_weight=effective_weight,
            )
        )
    return result


@app.patch("/sources/{source_id}", response_model=dict[str, Any])
def patch_source(
    source_id: str,
    body: SourceOverrideUpdate,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Upsert a SourceOverride — toggle active or set weight_override."""
    existing = db.query(SourceOverride).filter(SourceOverride.source_id == source_id).first()
    if existing:
        if body.active is not None:
            existing.active = body.active
        if body.weight_override is not None:
            existing.weight_override = body.weight_override
    else:
        existing = SourceOverride(
            source_id=source_id,
            active=body.active if body.active is not None else True,
            weight_override=body.weight_override,
        )
        db.add(existing)
    db.commit()
    db.refresh(existing)
    return {
        "source_id": existing.source_id,
        "active": existing.active,
        "weight_override": existing.weight_override,
    }


@app.post("/sources/{source_id}/enable", response_model=dict[str, Any])
def enable_source(source_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Convenience endpoint to enable a source."""
    return patch_source(source_id, SourceOverrideUpdate(active=True), db)


@app.post("/sources/{source_id}/disable", response_model=dict[str, Any])
def disable_source(source_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Convenience endpoint to disable a source."""
    return patch_source(source_id, SourceOverrideUpdate(active=False), db)


# ─── Custom Sources CRUD ──────────────────────────────────────────────────────

@app.get("/sources/custom", response_model=list[CustomSourceSchema])
def list_custom_sources(db: Session = Depends(get_db)) -> list[CustomSource]:
    """List all custom sources from DB (YAML-based ones are shown via GET /sources)."""
    return db.query(CustomSource).all()


@app.post("/sources/custom", response_model=CustomSourceSchema, status_code=201)
async def create_custom_source(
    body: CustomSourceCreate,
    db: Session = Depends(get_db),
) -> CustomSource:
    """Add a new custom source. Auto-generates slug id and auto-discovers RSS if needed."""
    if not body.url or not body.url.startswith("http"):
        raise HTTPException(status_code=400, detail="url must be a valid http(s) URL")
    if not _is_safe_url(body.url):
        raise HTTPException(status_code=400, detail="url must be a publicly reachable http(s) URL")

    # Generate id (slugify name)
    base_id = _slugify(body.name)
    source_id = _unique_id(base_id, db)

    # Auto-discover RSS if not provided
    rss_url = body.rss_url
    if not rss_url:
        try:
            async with httpx.AsyncClient() as client:
                rss_url = await autodiscover_rss(body.url, client)
        except Exception as exc:  # noqa: BLE001
            logger.warning("RSS autodiscovery failed for %s: %s", body.url, exc)
            rss_url = None

    record = CustomSource(
        id=source_id,
        name=body.name,
        url=body.url,
        rss_url=rss_url,
        category=body.category or "custom",
        type=body.type or "blog",
        language="en",
        weight=body.weight if body.weight is not None else 1.2,
        active=True,
        added_at=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.patch("/sources/custom/{source_id}", response_model=CustomSourceSchema)
def update_custom_source(
    source_id: str,
    body: CustomSourceUpdate,
    db: Session = Depends(get_db),
) -> CustomSource:
    """Update a custom source."""
    record = db.query(CustomSource).filter(CustomSource.id == source_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Custom source not found")
    if body.name is not None:
        record.name = body.name
    if body.url is not None:
        record.url = body.url
    if body.rss_url is not None:
        record.rss_url = body.rss_url
    if body.weight is not None:
        record.weight = body.weight
    if body.active is not None:
        record.active = body.active
    db.commit()
    db.refresh(record)
    return record


@app.delete("/sources/custom/{source_id}", status_code=204)
def delete_custom_source(source_id: str, db: Session = Depends(get_db)) -> None:
    """Delete a custom source from the DB.

    Returns 409 if the source only exists in custom_sources.yaml (can't delete via API).
    """
    record = db.query(CustomSource).filter(CustomSource.id == source_id).first()
    if not record:
        # Check if it's a YAML-based custom source
        try:
            with open(settings.custom_sources_yaml, "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            yaml_ids = [s["id"] for s in (data.get("sources") or [])]
            if source_id in yaml_ids:
                raise HTTPException(
                    status_code=409,
                    detail="Edit sources/custom_sources.yaml to remove file-based entries",
                )
        except HTTPException:
            raise
        except Exception:  # noqa: BLE001
            pass
        raise HTTPException(status_code=404, detail="Custom source not found")
    db.delete(record)
    db.commit()


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


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _slugify(text: str) -> str:
    """Convert a display name to a URL-safe kebab-case id."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text.strip())
    text = re.sub(r"-+", "-", text)
    return text[:64]


def _unique_id(base: str, db: Session) -> str:
    """Ensure slug uniqueness in the custom_sources table."""
    candidate = base
    counter = 2
    while db.query(CustomSource).filter(CustomSource.id == candidate).first():
        candidate = f"{base}-{counter}"
        counter += 1
    return candidate


# ─── Seed sources from YAML ───────────────────────────────────────────────────

def _seed_sources() -> None:
    """Insert official sources from YAML into DB (upsert by id)."""
    from app.db import SessionLocal

    sources = load_official_sources()
    if not sources:
        logger.warning("Official sources YAML not found or empty — skipping seed")
        return

    db = SessionLocal()
    try:
        for entry in sources:
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
