# AI Pulse — Roadmap

## ✅ Completed (Steps 1–4)

- [x] Repo scaffold (README, LICENSE, .gitignore, docker-compose.yml)
- [x] Source catalog — `sources/top_100_ai_sources.yaml` (100 entries, now 103)
- [x] Backend MVP — FastAPI + SQLAlchemy + scrapers + ranking + summariser + scheduler
- [x] Mobile scaffold — Expo + expo-router Feed/Detail/Settings screens
- [x] Docs — Architecture diagram + Roadmap
- [x] Custom sources API — `POST/PATCH/DELETE /sources/custom`, `PATCH /sources/{id}`, `sources_loader.py`

---

## Step 5 — Summariser wiring & API keys ✅

- [x] Wire `GROQ_API_KEY` — primary summariser (llama-3.3-70b-versatile, free tier)
- [x] Wire `ANTHROPIC_API_KEY` — Claude claude-haiku-4-5-20251001 fallback
- [x] Wire `OPENAI_API_KEY` — gpt-4o-mini fallback
- [x] Wire `MISTRAL_API_KEY` — mistral-small-latest fallback
- [x] Wire `TOGETHER_API_KEY` — Llama-3.3-70B-Instruct-Turbo fallback
- [x] Wire `GEMINI_API_KEY` — gemini-2.0-flash last LLM fallback
- [x] 6-provider chain with extractive safety net (Groq → Anthropic → OpenAI → Mistral → Together → Gemini → Extractive)
- [x] Per-provider logging (provider name, model, chars)

## Step 6 — Scheduler live & pipeline hardening

- [x] GitHub Actions CI runs `pytest` on every PR and push to `main`
- [x] Add pipeline run metadata table (run_at, articles_fetched, articles_selected)
- [x] Add `/pipeline/run` admin endpoint (POST, protected with API key)
- [x] Expose pipeline status via `/pipeline/status`

- [ ] Smoke-test the full pipeline against live RSS feeds
- [ ] Handle sources with no RSS (html.py fallback for sites like DeepMind Blog)

## Step 7 — Docker Compose polish

- [ ] Add health-check for the backend container
- [ ] Uncomment Postgres service and test with `DATABASE_URL=postgresql://...`
- [ ] Add `nginx` reverse-proxy service (optional)
- [ ] Write `docker-compose.prod.yml` override

## Step 8 — Mobile screens & UX

- [ ] Implement Settings screen: API base URL, notification toggle, theme
- [ ] Add bookmark / save-for-later feature (AsyncStorage)
- [ ] Add category filter chips on the Feed screen
- [ ] Implement share sheet (React Native Share)
- [ ] Add pull-to-refresh animation and empty state illustrations
- [ ] Offline support: cache last successful fetch with AsyncStorage

## Step 9 — Push notifications via FCM

- [ ] Set up Firebase project and obtain `google-services.json` / `GoogleService-Info.plist`
- [ ] Configure `expo-notifications` for FCM
- [ ] Backend: store push tokens per device (`PushToken` model)
- [ ] Backend: `POST /push/register` endpoint
- [ ] After daily pipeline run: send push notification with top story headline
- [ ] Add `expo-task-manager` background fetch (optional)

## Step 10 — Deploy Railway + EAS

- [ ] Create Railway project, add Postgres add-on
- [ ] Set env vars in Railway dashboard
- [ ] Create `railway.toml` / `Procfile`
- [ ] Configure EAS Build profiles (`eas.json`)
- [ ] Submit to App Store Connect (TestFlight) and Google Play Internal Testing
- [ ] Set up CI/CD: GitHub Actions → run `pytest`, build Docker image, push to Railway
