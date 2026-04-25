"""Pipeline observability and manual trigger endpoints."""
from __future__ import annotations

import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import PipelineRun

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


def _serialize_run(run: PipelineRun) -> dict[str, Any]:
    def _iso(dt: Optional[datetime.datetime]) -> Optional[str]:
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt.astimezone(datetime.timezone.utc).isoformat()

    return {
        "id": run.id,
        "started_at": _iso(run.started_at),
        "finished_at": _iso(run.finished_at),
        "status": run.status,
        "articles_fetched": run.articles_fetched,
        "articles_selected": run.articles_selected,
        "trigger": run.trigger,
        "error": run.error,
    }


@router.post("/run")
def trigger_pipeline(
    x_admin_api_key: Optional[str] = Header(default=None, alias="X-Admin-Api-Key"),
) -> dict[str, Any]:
    """Trigger the daily pipeline manually. Protected by X-Admin-Api-Key header."""
    if not settings.admin_api_key:
        raise HTTPException(status_code=503, detail="Admin API key is not configured")
    if x_admin_api_key != settings.admin_api_key:
        raise HTTPException(status_code=401, detail="Invalid admin API key")

    from app import pipeline  # lazy import to avoid circular dependency at module level

    try:
        run = pipeline.run_daily(trigger="manual")
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Pipeline failed") from exc
    return _serialize_run(run)


@router.get("/status")
def pipeline_status(limit: int = 10, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Return the most recent pipeline runs, newest first."""
    limit = max(1, min(limit, 50))
    rows = (
        db.query(PipelineRun)
        .order_by(PipelineRun.started_at.desc())
        .limit(limit)
        .all()
    )
    return {"runs": [_serialize_run(r) for r in rows]}
