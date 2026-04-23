# AI Pulse — Architecture

## Pipeline overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      SOURCES (103+)                             │
│  Blogs · Substack · YouTube · Podcasts · Reddit · arXiv · HN   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SCRAPERS                                    │
│  rss.py (feedparser)  ·  reddit.py (JSON)  ·  hn.py (Algolia)  │
│  html.py (BeautifulSoup fallback)                               │
└────────────────────────┬────────────────────────────────────────┘
                         │  ArticleDraft[]
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DEDUPLICATE                                 │
│  Unique by URL                                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     RANKING                                     │
│  score = 0.4·recency + 0.3·source_weight                       │
│        + 0.2·keyword_relevance + 0.1·engagement               │
│  → Top 25                                                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SUMMARISER                                  │
│  1. Anthropic Claude Haiku 3.5 (primary)                        │
│  2. Gemini 2.0 Flash (fallback)                                 │
│  3. Extractive — first 3 sentences (no API)                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DATABASE                                    │
│  SQLite (dev) / PostgreSQL (prod)                               │
│  SQLAlchemy ORM — Source + Article tables                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FASTAPI BACKEND                             │
│  GET /health  ·  GET /sources  ·  GET /articles/today          │
│  GET /articles/{id}                                             │
└────────────────────────┬────────────────────────────────────────┘
                         │  JSON over HTTP
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     REACT NATIVE / EXPO                         │
│  Feed screen → Article detail → in-app browser                 │
│  expo-router  ·  expo-web-browser                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PUSH NOTIFICATIONS (future)                 │
│  expo-notifications → FCM → iOS/Android                        │
└─────────────────────────────────────────────────────────────────┘
```

## Scheduler

APScheduler `BackgroundScheduler` fires `pipeline.run_daily()` at **08:00** local time
(configurable via `DAILY_RUN_HOUR` env var).

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./news.db` | SQLAlchemy DB URL |
| `ANTHROPIC_API_KEY` | — | Anthropic Claude key |
| `GEMINI_API_KEY` | — | Google Gemini key |
| `TZ` | `Europe/Bucharest` | Local timezone for scheduler |
| `DAILY_RUN_HOUR` | `8` | Hour of day to run pipeline |

## Deployment (planned)

| Service | Platform |
|---------|----------|
| Backend API | Railway |
| Mobile build | Expo EAS |
| Database (prod) | Railway Postgres |

## Custom Sources

Users can extend the source catalog without modifying the official YAML. The loader
merges sources in this order (later entry wins on duplicate `id`):

```
official YAML → custom YAML → custom DB → overrides DB
```

| Layer | File / Table | Who edits it |
|-------|-------------|--------------|
| Official catalog | `sources/top_100_ai_sources.yaml` | Maintainers (PR) |
| Custom YAML | `sources/custom_sources.yaml` | User (git edit) |
| Custom DB | `custom_sources` table | `POST /sources/custom` API |
| Overrides | `source_overrides` table | `PATCH /sources/{id}` API |

`load_all_sources()` in `backend/app/sources_loader.py` performs the merge and applies
`SourceOverride` active / weight_override values before returning the effective list.
The pipeline skips any source where `effective_active == False`.

