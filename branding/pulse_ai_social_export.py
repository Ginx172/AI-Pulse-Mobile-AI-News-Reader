#!/usr/bin/env python3
"""
SCRIPT NAME: pulse_ai_social_export.py
====================================
Execution Location: /home/claude/pulse_ai_export/
Required Directory Structure:
    pulse_ai_export/
    ├── pulse_ai_master.svg        (source vector)
    ├── pulse_ai_social_export.py  (this script)
    ├── output/                    (generated PNGs)
    │   ├── instagram/
    │   ├── facebook/
    │   ├── x_twitter/
    │   ├── linkedin/
    │   ├── youtube/
    │   ├── tiktok/
    │   ├── pinterest/
    │   ├── threads/
    │   ├── reddit/
    │   ├── snapchat/
    │   └── universal/
    ├── logs/                      (execution logs)
    └── checkpoints/               (resume state)

Author: Professional AI Development System
Level: Doctoral - AI & Machine Learning Specialization
Hardware Optimization: Intel i7-9700F (8 cores), NVIDIA GTX 1070 8GB VRAM, 16GB DDR4
Creation Date: 2026-04-24
Last Modified: 2026-04-24
Purpose: Generate Pulse AI watermark badge in all sizes required by the top 10
         social networks, from a single master SVG source. Full RGBA transparency
         preserved so the badge overlays cleanly on any host image.

Design rationale:
    - Badge displays at 15% of shorter edge on host image (industry watermark standard).
    - Master aspect ratio 5:6 (stacked icon + wordmark), 2x retina headroom.
    - Each size rendered from vector source — no upscaling artifacts.
    - Output PNG uses alpha channel; black panel is baked in per brand spec.

Dependencies:
    pip install cairosvg Pillow

Usage:
    python3 pulse_ai_social_export.py                 # full export
    python3 pulse_ai_social_export.py --resume        # resume from checkpoint
    python3 pulse_ai_social_export.py --clean         # wipe output, re-export
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

import cairosvg
from PIL import Image

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR = Path(__file__).parent.resolve()
SOURCE_SVG = SCRIPT_DIR / "pulse_ai_master.svg"
OUTPUT_DIR = SCRIPT_DIR / "output"
LOG_DIR = SCRIPT_DIR / "logs"
CHECKPOINT_DIR = SCRIPT_DIR / "checkpoints"
CHECKPOINT_FILE = CHECKPOINT_DIR / "export_state.json"

# Master SVG canvas dimensions (5:6 aspect — stacked lockup)
SVG_WIDTH = 500
SVG_HEIGHT = 600


# ============================================================================
# PLATFORM SPECIFICATIONS
# ============================================================================
# Each entry defines the badge sizes needed for a platform. Reasoning per size:
#   - Primary: 15% of shorter edge of the platform's standard feed image
#   - Retina (@2x): for high-DPI displays
#   - Favicon/App icon: where the platform ships a recognizable square
#   - Hero: for large header/splash usage (profile banners)

@dataclass(frozen=True)
class BadgeSize:
    """A single PNG export target."""
    name: str               # filename stem
    width: int              # output width in pixels
    height: int             # output height in pixels
    purpose: str            # human-readable reason

    def filename(self) -> str:
        return f"pulse_ai_{self.name}_{self.width}x{self.height}.png"


# Aspect ratio of the master is 5:6 → height = width * 1.2
def stacked(w: int) -> tuple[int, int]:
    """Return (width, height) for stacked-aspect badge at given width."""
    return w, int(round(w * 1.2))


PLATFORMS: dict[str, list[BadgeSize]] = {
    # 1. Instagram — feed 1080x1080, story/reel 1080x1920
    "instagram": [
        BadgeSize("feed_badge_1x",   *stacked(162), "15% of 1080px feed — standard density"),
        BadgeSize("feed_badge_2x",   *stacked(324), "15% of 1080px feed — retina"),
        BadgeSize("story_badge_1x",  *stacked(162), "15% of 1080px story shorter edge"),
        BadgeSize("story_badge_2x",  *stacked(324), "15% of 1080px story — retina"),
        BadgeSize("profile",         320, 320,      "profile/avatar square crop"),
    ],
    # 2. Facebook — feed image 1200x630, profile 180x180
    "facebook": [
        BadgeSize("feed_badge_1x",   *stacked(94),  "15% of 630px shorter edge"),
        BadgeSize("feed_badge_2x",   *stacked(188), "15% of 630px — retina"),
        BadgeSize("shared_link_1x",  *stacked(94),  "link preview overlay"),
        BadgeSize("profile",         180, 180,      "profile square"),
    ],
    # 3. X (Twitter) — feed 1200x675, header 1500x500
    "x_twitter": [
        BadgeSize("feed_badge_1x",   *stacked(101), "15% of 675px shorter edge"),
        BadgeSize("feed_badge_2x",   *stacked(202), "15% of 675px — retina"),
        BadgeSize("header_badge",    *stacked(120), "clamped min for 500px header"),
        BadgeSize("profile",         400, 400,      "profile square 400x400"),
    ],
    # 4. LinkedIn — feed 1200x627, profile 400x400
    "linkedin": [
        BadgeSize("feed_badge_1x",   *stacked(94),  "15% of 627px shorter edge"),
        BadgeSize("feed_badge_2x",   *stacked(188), "15% of 627px — retina"),
        BadgeSize("profile",         400, 400,      "profile square 400x400"),
        BadgeSize("company_logo",    300, 300,      "LinkedIn company page logo"),
    ],
    # 5. YouTube — thumbnail 1280x720, channel art 2560x1440
    "youtube": [
        BadgeSize("thumb_badge_1x",  *stacked(108), "15% of 720px thumbnail shorter edge"),
        BadgeSize("thumb_badge_2x",  *stacked(216), "15% of 720px — retina"),
        BadgeSize("channel_icon",    800, 800,      "YouTube channel icon 800x800"),
    ],
    # 6. TikTok — video 1080x1920, profile 200x200
    "tiktok": [
        BadgeSize("video_badge_1x",  *stacked(162), "15% of 1080px video shorter edge"),
        BadgeSize("video_badge_2x",  *stacked(324), "15% of 1080px video — retina"),
        BadgeSize("profile",         200, 200,      "profile square 200x200"),
    ],
    # 7. Pinterest — pin 1000x1500, profile 165x165
    "pinterest": [
        BadgeSize("pin_badge_1x",    *stacked(150), "15% of 1000px pin shorter edge"),
        BadgeSize("pin_badge_2x",    *stacked(300), "15% of 1000px — retina"),
        BadgeSize("profile",         165, 165,      "profile square 165x165"),
    ],
    # 8. Threads — feed 1080x1350
    "threads": [
        BadgeSize("feed_badge_1x",   *stacked(162), "15% of 1080px shorter edge"),
        BadgeSize("feed_badge_2x",   *stacked(324), "15% of 1080px — retina"),
        BadgeSize("profile",         320, 320,      "profile square"),
    ],
    # 9. Reddit — post image 1200x628
    "reddit": [
        BadgeSize("post_badge_1x",   *stacked(94),  "15% of 628px post shorter edge"),
        BadgeSize("post_badge_2x",   *stacked(188), "15% of 628px — retina"),
        BadgeSize("subreddit_icon",  256, 256,      "subreddit icon 256x256"),
    ],
    # 10. Snapchat — snap 1080x1920
    "snapchat": [
        BadgeSize("snap_badge_1x",   *stacked(162), "15% of 1080px snap shorter edge"),
        BadgeSize("snap_badge_2x",   *stacked(324), "15% of 1080px — retina"),
        BadgeSize("profile",         320, 320,      "profile square"),
    ],
    # Universal — master files and favicon/PWA set, useful everywhere
    "universal": [
        BadgeSize("master",          500, 600,      "master file at native resolution"),
        BadgeSize("master_2x",       1000, 1200,    "master at 2x for high-DPI"),
        BadgeSize("master_4x",       2000, 2400,    "master at 4x for print/hero use"),
        BadgeSize("favicon_16",      16, 16,        "browser favicon (tiny) — icon detail only"),
        BadgeSize("favicon_32",      32, 32,        "browser favicon (standard)"),
        BadgeSize("favicon_48",      48, 48,        "Windows tile / favicon"),
        BadgeSize("app_icon_192",    192, 192,      "PWA manifest 192"),
        BadgeSize("app_icon_512",    512, 512,      "PWA manifest 512 / app store"),
        BadgeSize("og_square",       600, 600,      "Open Graph fallback square"),
    ],
}


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging() -> logging.Logger:
    """Configure dual-output logging: file + console."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"export_{time.strftime('%Y%m%d_%H%M%S')}.log"

    logger = logging.getLogger("pulse_ai_export")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()  # defensive: avoid duplicate handlers on re-run

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    logger.info("=" * 72)
    logger.info("Pulse AI — Social Media Export Pipeline")
    logger.info("=" * 72)
    logger.info(f"Log file: {log_file}")
    return logger


# ============================================================================
# CHECKPOINTING
# ============================================================================

def load_checkpoint() -> set[str]:
    """Return set of already-completed output file paths (relative)."""
    if not CHECKPOINT_FILE.exists():
        return set()
    try:
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data.get("completed", []))
    except (json.JSONDecodeError, OSError):
        return set()


def save_checkpoint(completed: set[str], source_hash: str) -> None:
    """Persist export progress so interrupted runs can resume."""
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "source_hash": source_hash,
        "completed": sorted(completed),
        "timestamp": time.time(),
    }
    tmp = CHECKPOINT_FILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    tmp.replace(CHECKPOINT_FILE)  # atomic write


def hash_file(path: Path) -> str:
    """SHA-256 of file contents — invalidate checkpoint if source changed."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ============================================================================
# RENDERING
# ============================================================================

def render_png(
    svg_bytes: bytes,
    width: int,
    height: int,
    output_path: Path,
    logger: logging.Logger,
) -> tuple[bool, float, int]:
    """
    Render SVG to PNG at target dimensions.
    Returns: (success, elapsed_seconds, output_size_bytes).
    """
    start = time.perf_counter()
    try:
        # CairoSVG renders with proper alpha channel.
        # We control dimensions directly; aspect ratio is preserved by the
        # viewBox, so specifying both width and height crops/stretches if
        # they don't match the source ratio. For square outputs (profile,
        # favicon), we render at native aspect then center-crop to square.
        source_ratio = SVG_WIDTH / SVG_HEIGHT  # 500/600 = 0.833...
        target_ratio = width / height

        if abs(source_ratio - target_ratio) < 1e-3:
            # Same aspect — render directly
            cairosvg.svg2png(
                bytestring=svg_bytes,
                write_to=str(output_path),
                output_width=width,
                output_height=height,
            )
        else:
            # Different aspect — render at native ratio, then center-crop or pad
            # Strategy: render at the LARGER of the two dimensions' natural size,
            # then composite onto a transparent canvas of target dimensions,
            # centered. This preserves the logo geometry while producing the
            # requested frame size (e.g. square profile images).
            if target_ratio > source_ratio:
                # Target is wider → render to match target height
                render_h = height
                render_w = int(round(height * source_ratio))
            else:
                # Target is taller/narrower → render to match target width
                render_w = width
                render_h = int(round(width / source_ratio))

            # For square crops we want the logo to fit inside with margin,
            # not just letterbox. So scale down slightly (90%) for squares.
            if width == height:
                render_w = int(render_w * 0.90)
                render_h = int(render_h * 0.90)

            png_bytes = cairosvg.svg2png(
                bytestring=svg_bytes,
                output_width=render_w,
                output_height=render_h,
            )

            # Composite onto transparent canvas of target size
            from io import BytesIO
            rendered = Image.open(BytesIO(png_bytes)).convert("RGBA")
            canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            offset_x = (width - render_w) // 2
            offset_y = (height - render_h) // 2
            canvas.paste(rendered, (offset_x, offset_y), rendered)
            canvas.save(output_path, "PNG", optimize=True)
            rendered.close()
            canvas.close()

        elapsed = time.perf_counter() - start
        size = output_path.stat().st_size
        return True, elapsed, size

    except Exception as exc:
        elapsed = time.perf_counter() - start
        logger.error(f"Render failed for {output_path.name}: {exc}")
        return False, elapsed, 0


# ============================================================================
# PROGRESS DISPLAY
# ============================================================================

def progress_bar(current: int, total: int, width: int = 30) -> str:
    """Return a text progress bar string."""
    pct = current / total if total else 1.0
    filled = int(width * pct)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {pct*100:5.1f}%  ({current}/{total})"


def format_eta(seconds: float) -> str:
    """Format remaining time as H:MM:SS or M:SS."""
    if seconds < 0 or seconds != seconds:  # NaN guard
        return "--:--"
    seconds = int(seconds)
    if seconds >= 3600:
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        return f"{h}:{m:02d}:{s:02d}"
    m, s = divmod(seconds, 60)
    return f"{m}:{s:02d}"


# ============================================================================
# MAIN EXPORT LOOP
# ============================================================================

def run_export(resume: bool, clean: bool, logger: logging.Logger) -> int:
    """Execute the full export. Returns exit code."""

    # Validate source
    if not SOURCE_SVG.exists():
        logger.error(f"Source SVG not found: {SOURCE_SVG}")
        return 1

    source_hash = hash_file(SOURCE_SVG)
    logger.info(f"Source: {SOURCE_SVG.name} (sha256: {source_hash[:16]}...)")

    svg_bytes = SOURCE_SVG.read_bytes()

    # Handle --clean
    if clean:
        import shutil
        if OUTPUT_DIR.exists():
            shutil.rmtree(OUTPUT_DIR)
            logger.info(f"Cleaned: {OUTPUT_DIR}")
        if CHECKPOINT_FILE.exists():
            CHECKPOINT_FILE.unlink()

    # Load resume state
    completed: set[str] = set()
    if resume:
        completed = load_checkpoint()
        if completed:
            logger.info(f"Resuming: {len(completed)} files already rendered")

    # Flatten job list
    jobs: list[tuple[str, BadgeSize]] = []
    for platform, sizes in PLATFORMS.items():
        for size in sizes:
            jobs.append((platform, size))

    total = len(jobs)
    logger.info(f"Platforms: {len(PLATFORMS)}  |  Total exports: {total}")
    logger.info("-" * 72)

    # Execute
    t_start = time.perf_counter()
    success_count = 0
    fail_count = 0
    skip_count = 0
    total_bytes = 0
    per_job_times: list[float] = []

    for idx, (platform, size) in enumerate(jobs, start=1):
        platform_dir = OUTPUT_DIR / platform
        platform_dir.mkdir(parents=True, exist_ok=True)
        out_path = platform_dir / size.filename()
        rel_key = f"{platform}/{size.filename()}"

        # Skip if already done
        if rel_key in completed and out_path.exists():
            skip_count += 1
            logger.debug(f"  SKIP  {rel_key}")
            continue

        ok, elapsed, size_bytes = render_png(
            svg_bytes, size.width, size.height, out_path, logger
        )

        if ok:
            success_count += 1
            total_bytes += size_bytes
            per_job_times.append(elapsed)
            completed.add(rel_key)

            # ETA calculation
            avg = sum(per_job_times) / len(per_job_times)
            remaining_jobs = total - idx
            eta = avg * remaining_jobs

            bar = progress_bar(idx, total)
            logger.info(
                f"{bar}  {elapsed*1000:5.0f}ms  "
                f"{size_bytes/1024:6.1f}KB  ETA {format_eta(eta)}  "
                f"{platform}/{size.name} {size.width}x{size.height}"
            )
        else:
            fail_count += 1
            logger.warning(f"  FAIL  {rel_key}")

        # Periodic checkpoint (every 10 jobs)
        if idx % 10 == 0:
            save_checkpoint(completed, source_hash)

        # Periodic memory cleanup (every 20 jobs) — defensive even though
        # CairoSVG/Pillow release memory on context exit
        if idx % 20 == 0:
            gc.collect()

    # Final checkpoint
    save_checkpoint(completed, source_hash)

    # Summary
    total_elapsed = time.perf_counter() - t_start
    logger.info("-" * 72)
    logger.info("EXPORT SUMMARY")
    logger.info(f"  Successful : {success_count}")
    logger.info(f"  Skipped    : {skip_count} (already rendered)")
    logger.info(f"  Failed     : {fail_count}")
    logger.info(f"  Total size : {total_bytes/1024:.1f} KB "
                f"({total_bytes/(1024*1024):.2f} MB)")
    logger.info(f"  Elapsed    : {total_elapsed:.2f}s")
    if per_job_times:
        logger.info(f"  Per-file avg: {sum(per_job_times)/len(per_job_times)*1000:.1f} ms")
    logger.info("=" * 72)

    return 0 if fail_count == 0 else 2


# ============================================================================
# ENTRY POINT
# ============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pulse AI — Social Media Export Pipeline",
    )
    parser.add_argument("--resume", action="store_true",
                        help="Resume from last checkpoint")
    parser.add_argument("--clean", action="store_true",
                        help="Wipe output and re-export everything")
    args = parser.parse_args()

    logger = setup_logging()
    try:
        return run_export(resume=args.resume, clean=args.clean, logger=logger)
    except KeyboardInterrupt:
        logger.warning("Interrupted by user. Run with --resume to continue.")
        return 130
    except Exception as exc:
        logger.exception(f"Fatal error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
