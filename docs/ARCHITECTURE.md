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
│  1. Groq llama-3.3-70b-versatile (primary — free tier)          │
│  2. Anthropic claude-haiku-4-5-20251001 (high quality, cheap)   │
│  3. OpenAI gpt-4o-mini (premium fallback)                       │
│  4. Mistral mistral-small-latest                                 │
│  5. Together AI Llama-3.3-70B-Instruct-Turbo                    │
│  6. Gemini 2.0 Flash (free fallback when quota OK)              │
│  7. Extractive — first 3 sentences (no API)                     │
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
│                     NEXT.JS 15 PWA                              │
│  Feed (/) → Article detail → Settings + Manage Sources         │
│  App Router  ·  TailwindCSS  ·  shadcn/ui  ·  next-pwa         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PUSH NOTIFICATIONS (future)                 │
│  Web Push API → Service Worker                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Scheduler

APScheduler `BackgroundScheduler` fires `pipeline.run_daily()` at **08:00** local time
(configurable via `DAILY_RUN_HOUR` env var).

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./news.db` | SQLAlchemy DB URL |
| `GROQ_API_KEY` | — | Groq key (primary summariser) |
| `ANTHROPIC_API_KEY` | — | Anthropic Claude key |
| `OPENAI_API_KEY` | — | OpenAI key |
| `MISTRAL_API_KEY` | — | Mistral AI key |
| `TOGETHER_API_KEY` | — | Together AI key |
| `GEMINI_API_KEY` | — | Google Gemini key |
| `TZ` | `Europe/Bucharest` | Local timezone for scheduler |
| `DAILY_RUN_HOUR` | `8` | Hour of day to run pipeline |

## Deployment (planned)

| Service | Platform |
|---------|----------|
| Backend API | Railway |
| Web app | Vercel / any Node host |
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

