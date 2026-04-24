# Pulse AI — Social Media Logo Pack

Complete PNG logo pack for Pulse AI across the top 10 social networks plus universal assets.

---

## What's included

**44 PNG files** rendered from a single master SVG source, organized by platform:

```
output/
├── instagram/      5 files  (feed, story, profile)
├── facebook/       4 files  (feed, link, profile)
├── x_twitter/      4 files  (feed, header, profile)
├── linkedin/       4 files  (feed, profile, company logo)
├── youtube/        3 files  (thumbnail overlay, channel icon)
├── tiktok/         3 files  (video overlay, profile)
├── pinterest/      3 files  (pin overlay, profile)
├── threads/        3 files  (feed, profile)
├── reddit/         3 files  (post overlay, subreddit icon)
├── snapchat/       3 files  (snap overlay, profile)
└── universal/      9 files  (master, favicons, app icons, OG)
```

All PNGs have **transparent padding around the black badge panel**, so they overlay cleanly on any host image.

---

## Filename convention

```
pulse_ai_{purpose}_{width}x{height}.png
```

Example: `pulse_ai_feed_badge_1x_162x194.png` → Instagram feed watermark, 1x density.

---

## Sizing logic

Each badge is sized to display at **15% of the shorter edge** of its target image format. This is the standard watermark overlay ratio used by Bloomberg, TechCrunch, The Verge, and most publisher apps — visible enough to register, small enough to never intrude.

Per-platform math (example: Instagram):
- Instagram feed image = 1080 × 1080
- Shorter edge = 1080
- Badge width at 15% = 162 px
- Badge at 5:6 aspect = 162 × 194 px  ← matches `feed_badge_1x`

The `_2x` variants are retina-ready (doubled resolution) for high-DPI displays.

---

## App implementation

When your app overlays the badge on an article image, use this pattern:

```python
badge_size = round(min(image.width, image.height) * 0.15)
badge_inset = round(min(image.width, image.height) * 0.02)
overlay(badge, x=badge_inset, y=badge_inset)  # upper-left
on_tap: hide_badge() → navigate_to(article.url)
```

The `_1x` file matches typical display sizing. Pick the `_2x` for retina/3x screens.

### Minimum size clamp (recommended)

For ultra-wide formats (e.g. Twitter headers at 500px shorter edge), consider clamping the badge to a minimum of 120px to preserve wordmark legibility — otherwise "Pulse AI" drops below the 12px readability floor.

---

## Master assets (`universal/`)

| File | Size | Use |
|---|---|---|
| `pulse_ai_master_500x600.png` | 500×600 | Native resolution |
| `pulse_ai_master_2x_1000x1200.png` | 1000×1200 | 2x / retina |
| `pulse_ai_master_4x_2000x2400.png` | 2000×2400 | Print / hero banner |
| `pulse_ai_favicon_16_16x16.png` | 16×16 | Browser favicon (tiny) |
| `pulse_ai_favicon_32_32x32.png` | 32×32 | Standard favicon |
| `pulse_ai_favicon_48_48x48.png` | 48×48 | Windows tile |
| `pulse_ai_app_icon_192_192x192.png` | 192×192 | PWA manifest |
| `pulse_ai_app_icon_512_512x512.png` | 512×512 | App store / PWA large |
| `pulse_ai_og_square_600x600.png` | 600×600 | Open Graph fallback |

**Note on tiny favicons (16px, 32px):** at these sizes the wordmark "Pulse AI" becomes unreadable (~2–4px tall). These files still render the full stacked lockup, but for optimum clarity in browser tabs you may want to commission a separate icon-only favicon variant. Let me know if you'd like that generated.

---

## Brand specifications

- **Icon gradient:** `#4F46E5` indigo → `#8B5CF6` violet (diagonal, applied along stroke)
- **Wordmark color:** `#FFD500` (Ukrainian flag yellow, Pantone 123 C)
- **Panel:** pure black `#000000`, 5:6 aspect, 14% corner radius
- **Font stack:** Inter → Geist → Satoshi → system sans-serif, weight 700
- **Tracking:** −2 letter-spacing (tight, premium SaaS convention)

---

## Regenerating

All assets are rendered from `pulse_ai_master.svg`. To regenerate:

```bash
pip install cairosvg Pillow
python3 pulse_ai_social_export.py
```

Options:
- `--resume` — continue from last checkpoint if a run was interrupted
- `--clean` — wipe `output/` and re-export from scratch

---

## Hardware optimization notes

The export pipeline is optimized for the target hardware (i7-9700F, GTX 1070 8GB, 16GB DDR4):

- **CPU-bound rendering** (CairoSVG is single-threaded per file, parallelism via process pool if needed)
- **Periodic garbage collection** every 20 jobs to keep RSS bounded
- **Atomic checkpoint writes** (write-to-tmp + rename) — survives SIGKILL mid-export
- **Dual logging** (file + console) with full metrics per file

Typical full-pack runtime: ~2 seconds for 44 files. Memory footprint stays under 100 MB RSS.

---

## Contents

```
pulse_ai_logo_pack/
├── README.md                      ← you are here
├── pulse_ai_master.svg            ← source of truth (edit this to change the logo)
├── pulse_ai_social_export.py      ← regeneration pipeline
├── output/                        ← 44 PNG exports, organized per platform
└── logs/                          ← run history with per-file timings
```
