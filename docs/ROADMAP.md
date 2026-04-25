# AI Pulse — Roadmap

## ✅ Completed (Steps 1–4)

- [x] Repo scaffold (README, LICENSE, .gitignore, docker-compose.yml)
- [x] Source catalog — `sources/top_100_ai_sources.yaml` (100 entries, now 103)
- [x] Backend MVP — FastAPI + SQLAlchemy + scrapers + ranking + summariser + scheduler
- [x] Mobile scaffold — Expo + expo-router Feed/Detail/Settings screens
- [x] Docs — Architecture diagram + Roadmap
- [x] Custom sources API — `POST/PATCH/DELETE /sources/custom`, `PATCH /sources/{id}`, `sources_loader.py`

---

## Step 5 — Summariser wiring & API keys

- [ ] Wire `ANTHROPIC_API_KEY` in `.env` and validate Claude Haiku responses end-to-end
- [ ] Wire `GEMINI_API_KEY` and validate Gemini Flash fallback
- [ ] Add rate-limiting / retry logic for LLM calls
- [ ] Log token usage per pipeline run

## Step 6 — Scheduler live & pipeline hardening

- [x] GitHub Actions CI runs `pytest` on every PR and push to `main`

- [ ] Smoke-test the full pipeline against live RSS feeds
- [ ] Handle sources with no RSS (html.py fallback for sites like DeepMind Blog)
- [ ] Add pipeline run metadata table (run_at, articles_fetched, articles_selected)
- [ ] Add `/pipeline/run` admin endpoint (POST, protected with API key)
- [ ] Expose pipeline status via `/pipeline/status`

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
