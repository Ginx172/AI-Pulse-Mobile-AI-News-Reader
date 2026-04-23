# AI Pulse — Mobile AI News Reader

> *Product overview document — English / Markdown*

---

## 📌 Short Description

> **AI Pulse** — A mobile-first news reader that aggregates, filters, and summarizes the **Top 100 AI information sources** (research labs, blogs, newsletters, podcasts, YouTube channels, arXiv, GitHub trending) into a clean, distraction-free feed you can read anywhere on your phone.

**One-line tagline:**
> Stay on top of AI — 100 trusted sources, one feed, summarized for your phone.

**GitHub topics / tags:**
`ai-news` · `news-aggregator` · `mobile-app` · `react-native` · `rss` · `llm-summarization` · `arxiv` · `podcast` · `offline-reading` · `personalized-feed` · `android` · `ios`

---

## 📖 Extended Description

**AI Pulse** is a cross-platform mobile application that solves a problem every AI practitioner, researcher, and enthusiast faces today: **AI news is scattered across hundreds of sources and moves faster than any single human can track**.

The app continuously pulls content from a curated list of the **Top 100 AI information sources** — official lab blogs (OpenAI, Anthropic, DeepMind, Google Research, Meta AI, Microsoft Research, Mistral, Hugging Face), arXiv papers, flagship newsletters (Import AI, The Batch, Ben's Bites, TLDR AI), podcasts (Lex Fridman, Latent Space, No Priors, TWIML), YouTube channels (Two Minute Papers, Yannic Kilcher, 3Blue1Brown), Reddit, Hacker News AI threads, GitHub trending, and policy/safety outlets.

### 🎯 What it does

1. **Aggregates** — Pulls articles, papers, releases, and videos from 100 hand-picked AI sources via RSS, Atom, public APIs, and lightweight scrapers.
2. **Deduplicates** — Detects when multiple outlets cover the same story and groups them into a single card.
3. **Summarizes** — Uses an LLM to generate a 3–5 sentence TL;DR for each item.
4. **Ranks** — Scores items by source authority, recency, engagement signals, and the user's personal interests; selects the **top 25 per day**.
5. **Delivers** — Presents everything in a fast, swipeable, mobile-native feed with offline support and dark mode, plus a morning push notification.

### 🧩 Core Features

- **📰 Unified Feed** — All 100 sources merged into a single view, with category tabs (Research, Products, Funding, Open Source, Opinion, Tutorials, Podcasts, Videos).
- **🤖 AI-Powered TL;DRs** — Each article expanded into a quick summary so you can decide in seconds whether to read the full piece.
- **🔍 Smart Filters** — Filter by source, topic (LLMs, computer vision, robotics, multimodal, alignment, policy, hardware), reading time, or content type.
- **⭐ Personalization** — The app learns from your taps, saves, and reading time to surface what matters most to *you*.
- **📥 Offline Reading** — Auto-downloads your morning digest so you can read on the subway or on a plane.
- **🔔 Smart Notifications** — Daily digest, breaking news alerts, and "new paper from your followed authors" — never spammy.
- **🔖 Bookmarks & Read Later** — Save articles; export to Pocket / Instapaper / Notion / Readwise.
- **🎙️ Listen Mode** — Text-to-speech for any article, plus a built-in podcast player for the AI-podcast subset.
- **🌙 Dark Mode + Reader Mode** — Distraction-free reading optimized for phones.
- **🔒 Privacy-First** — No tracking, no ad networks, on-device personalization where possible; you own your data.

### 📚 The "Top 100 AI Sources" Curated List

The catalog is grouped into 8 buckets and version-controlled in this repository:

| Bucket | Examples |
|---|---|
| 🏛️ **Research Labs (Official)** | OpenAI, Anthropic, Google DeepMind, Meta AI, Microsoft Research, Hugging Face |
| 📄 **Academic / Papers** | arXiv (cs.AI, cs.LG, cs.CL, cs.CV), Papers with Code |
| 📧 **Newsletters / Substack** | Import AI, The Batch, Ben's Bites, TLDR AI, Last Week in AI, Interconnects, Latent Space |
| 📰 **Tech Press (AI)** | MIT Technology Review, Towards Data Science, Analytics Vidhya |
| 🎙️ **Podcasts** | Lex Fridman, Latent Space, No Priors, TWIML AI, Practical AI, Cognitive Revolution |
| 📺 **YouTube Channels** | Two Minute Papers, Yannic Kilcher, 3Blue1Brown, AI Explained, Andrej Karpathy |
| 💻 **Open-Source / Dev** | GitHub Trending AI, LangChain Blog, Hugging Face Trending |
| 🏛️ **Reddit & Aggregators** | r/MachineLearning, r/LocalLLaMA, Hacker News AI, Product Hunt AI |

The full machine-readable catalog lives in `sources/top_100_ai_sources.yaml` and powers the ingestion pipeline.

### 🛠️ Technical Stack

- **Mobile App:** React Native (Expo, TypeScript, expo-router) — single codebase for iOS + Android
- **Backend:** Python 3.11 + FastAPI + SQLAlchemy + APScheduler
- **Database:** SQLite (dev) / Postgres (prod)
- **Scrapers:** feedparser (RSS), httpx + BeautifulSoup (HTML), Reddit JSON, YouTube RSS, HN Algolia, arXiv RSS
- **Summarization (chain of fallback):**
  1. Anthropic Claude Haiku 3.5 (primary)
  2. Gemini 2.0 Flash (fallback, free tier)
  3. Extractive first-sentences (offline safety net)
- **Push:** expo-notifications → FCM
- **Hosting:** Railway (backend) + Expo EAS Build (mobile)

### 🚀 Roadmap

- [ ] **v0.1** — Source catalog (YAML) + ingestion pipeline + REST API
- [ ] **v0.2** — React Native MVP: feed, article view, bookmarks, dark mode
- [ ] **v0.3** — LLM summarization + dedupe + ranking top 25
- [ ] **v0.4** — Personalization, smart notifications, offline mode
- [ ] **v0.5** — Listen mode (TTS) + podcast player
- [ ] **v1.0** — Public release on Google Play and App Store

### 📜 License

Released under the **MIT License**. The curated source list is published under **CC-BY 4.0**.

---

*Status:* 🚧 Early development
*Document language:* English
*Format:* Markdown
