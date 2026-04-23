# AI Pulse — Mobile AI News Reader

> *Adapted from the [full product description](https://github.com/Ginx172/market-hawk/blob/copilot/top-100-ai-information-sources/AI_NEWS_READER_APP_DESCRIPTION.md).*

**AI Pulse** is a mobile-first AI news reader that aggregates the **Top 100 AI information sources** — research labs, arXiv, newsletters, Substack, podcasts, YouTube, Reddit, and open-source communities — deduplicates stories, ranks them, summarises them with an LLM, and serves the **top 25 daily** into a React Native mobile feed with push notifications and offline support.

## Repository layout

```
.
├── backend/          # Python 3.11 FastAPI backend
├── mobile/           # React Native + Expo (TypeScript, expo-router)
├── sources/          # Machine-readable catalog of 103 AI sources (YAML) + custom sources
└── docs/             # Architecture diagram, roadmap
```

## Quick start

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # fill in your API keys
uvicorn app.main:app --reload
```

API will be available at `http://localhost:8000`.  
Key endpoints:

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness probe |
| GET | `/sources` | All 103 sources from YAML |
| GET | `/articles/today` | Top 25 articles for today |
| GET | `/articles/{id}` | Single article detail |

### Mobile

```bash
cd mobile
npm install
npx expo start
```

### Docker Compose (backend + SQLite volume)

```bash
docker-compose up --build
```

## Pipeline overview

```
Sources YAML → Scrapers → Dedupe by URL → Ranker → Top 25 → Summariser → SQLite DB → FastAPI → Expo mobile
```

A daily APScheduler job fires at 08:00 (configurable) and runs the full pipeline.

## Tech stack

| Layer | Choice |
|-------|--------|
| Backend | Python 3.11, FastAPI, SQLAlchemy, SQLite (dev) / Postgres (prod) |
| Scheduler | APScheduler (cron, no Celery) |
| Scrapers | feedparser, httpx + BeautifulSoup, Reddit JSON, YouTube RSS |
| Summariser | Anthropic Claude Haiku 3.5 → Gemini 2.0 Flash → extractive fallback |
| Mobile | React Native + Expo (TypeScript, expo-router), EAS Build |
| Push | expo-notifications → FCM |
| Deploy | Railway (backend), Expo EAS (mobile) |

## License

Code: MIT — see [LICENSE](LICENSE).  
Source catalog: CC-BY-4.0 — see [sources/LICENSE](sources/LICENSE).
