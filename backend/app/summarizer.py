"""LLM summariser with a chain of fallbacks.

Chain:
  1. Anthropic Claude Haiku 3.5 (primary)
  2. Gemini 2.0 Flash (fallback)
  3. Extractive (first 3 cleaned sentences) — no API needed
"""
from __future__ import annotations

import logging
import re
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)

_PROMPT_TEMPLATE = (
    "Summarise the following article in 3–5 concise English sentences. "
    "Focus on the key finding, who made it, and why it matters for AI practitioners.\n\n"
    "Title: {title}\n\n"
    "Text: {text}"
)

_MAX_INPUT_CHARS = 4000  # Keep prompts short to save tokens


# ─── Provider implementations ─────────────────────────────────────────────────


def _summarise_anthropic(text: str, title: str) -> Optional[str]:
    """Call Anthropic Claude Haiku 3.5."""
    if not settings.anthropic_api_key:
        return None
    try:
        import anthropic  # type: ignore

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        message = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=300,
            messages=[
                {
                    "role": "user",
                    "content": _PROMPT_TEMPLATE.format(
                        title=title, text=text[:_MAX_INPUT_CHARS]
                    ),
                }
            ],
        )
        return message.content[0].text.strip()
    except Exception as exc:
        logger.warning("Anthropic summariser failed: %s", exc)
        return None


def _summarise_gemini(text: str, title: str) -> Optional[str]:
    """Call Gemini 2.0 Flash."""
    if not settings.gemini_api_key:
        return None
    try:
        import google.generativeai as genai  # type: ignore

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(
            _PROMPT_TEMPLATE.format(title=title, text=text[:_MAX_INPUT_CHARS])
        )
        return response.text.strip()
    except Exception as exc:
        logger.warning("Gemini summariser failed: %s", exc)
        return None


def _summarise_extractive(text: str, title: str) -> str:  # noqa: ARG001
    """Extractive fallback: return the first 3 non-empty sentences."""
    # Split on sentence-ending punctuation followed by whitespace/end
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    clean: list[str] = []
    for sent in sentences:
        sent = sent.strip()
        if len(sent) > 20:
            clean.append(sent)
        if len(clean) >= 3:
            break
    if not clean:
        # Last resort: return a truncated version of the text
        return (text[:300] + "…") if len(text) > 300 else text
    return " ".join(clean)


# ─── Public API ───────────────────────────────────────────────────────────────


def summarise(text: str, title: str = "") -> str:
    """Return a 3–5 sentence summary, using the best available provider.

    Falls back through: Anthropic → Gemini → Extractive.
    """
    if not text.strip():
        return title or "No content available."

    result = _summarise_anthropic(text, title)
    if result:
        return result

    result = _summarise_gemini(text, title)
    if result:
        return result

    return _summarise_extractive(text, title)
