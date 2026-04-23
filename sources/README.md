# AI Pulse — Top 103 AI Sources Catalog

This is the official curated list of **103 AI information sources** used by AI Pulse.
The app also supports user-added custom sources via `custom_sources.yaml` (see
[`docs/CUSTOM_SOURCES.md`](../docs/CUSTOM_SOURCES.md) for details).

## Schema

Each entry in `top_100_ai_sources.yaml` has the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | URL-safe kebab-case unique identifier |
| `name` | string | Human-readable display name |
| `url` | string | Canonical homepage URL |
| `rss_url` | string \| null | RSS/Atom feed URL; `null` if not confidently known |
| `category` | string | One of the 9 buckets (see below) |
| `type` | string | `blog`, `substack`, `youtube`, `podcast`, `reddit`, `arxiv`, `newsletter`, `aggregator` |
| `language` | string | ISO 639-1 language code (almost all `en`) |
| `weight` | float | Source quality weight for ranking (0.5–1.5) |

## Categories (9 buckets)

| Bucket | Description |
|--------|-------------|
| `research_lab` | Official blogs from major AI research labs |
| `blog` | Individual/company AI blogs and websites |
| `substack` | Substack newsletters |
| `youtube` | YouTube channels |
| `podcast` | Audio podcasts |
| `reddit` | Subreddits |
| `aggregator` | News aggregators, arXiv, GitHub Trending, etc. |
| `newsletter` | Email newsletters (non-Substack) |
| `podcasts` | Podcast shows (legacy alias for `podcast`) |
| `aggregators_misc` | Mixed community hubs and aggregators |
| `blogs_websites` | Blogs and data-science websites |

## Custom Sources

Users can add their own sources without editing this file. See
[`custom_sources.yaml`](custom_sources.yaml) and [`docs/CUSTOM_SOURCES.md`](../docs/CUSTOM_SOURCES.md)
for instructions.

## Adding an official source

1. Choose the next sequential ID in kebab-case.
2. Fill all required fields; set `rss_url: null` if you are not certain of the feed URL.
3. Keep `weight` between `0.5` (low quality) and `1.5` (flagship source).
4. Open a PR with your addition and update the entry count in this README.

## License

This catalog is licensed under **CC-BY-4.0** — see [LICENSE](LICENSE).
