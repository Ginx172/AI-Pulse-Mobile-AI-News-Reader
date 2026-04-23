"""APScheduler background scheduler.

Fires the daily pipeline at DAILY_RUN_HOUR (default 08:00 local time).
"""
from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def start_scheduler() -> None:
    """Start the APScheduler background scheduler (idempotent)."""
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        return

    from app.pipeline import run_daily  # avoid circular import at module level

    _scheduler = BackgroundScheduler(timezone=settings.tz)
    _scheduler.add_job(
        run_daily,
        trigger=CronTrigger(hour=settings.daily_run_hour, minute=0, timezone=settings.tz),
        id="daily_pipeline",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info(
        "Scheduler started — daily pipeline at %02d:00 %s",
        settings.daily_run_hour,
        settings.tz,
    )
