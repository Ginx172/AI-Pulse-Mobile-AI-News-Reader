"""LLM summariser with a chain of fallbacks.

Chain:
  1. Groq — llama-3.3-70b-versatile (rapid, free tier)
  2. Anthropic — claude-haiku-4-5-20251001 (high quality, cheap)
  3. OpenAI — gpt-4o-mini (premium fallback)
  4. Mistral — mistral-small-latest
  5. Together AI — meta-llama/Llama-3.3-70B-Instruct-Turbo
  6. Gemini — gemini-2.0-flash (free fallback when quota OK)
  7. Extractive (first 3 cleaned sentences) — no API needed
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


def _summarise_groq(text: str, title: str) -> Optional[str]:
    """Call Groq — llama-3.3-70b-versatile (free tier)."""
    if not settings.groq_api_key:
        return None
    try:
        from groq import Groq  # type: ignore

        client = Groq(api_key=settings.groq_api_key)
        model = "llama-3.3-70b-versatile"
        response = client.chat.completions.create(
            model=model,
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
        summary = response.choices[0].message.content.strip()
        logger.info("Groq summary OK (model=%s, chars=%d)", model, len(summary))
        return summary
    except Exception as exc:
        logger.warning("Groq summariser failed: %s", exc)
        return None


def _summarise_anthropic(text: str, title: str) -> Optional[str]:
    """Call Anthropic Claude Haiku 4.5."""
    if not settings.anthropic_api_key:
        return None
    try:
        import anthropic  # type: ignore

        model = "claude-haiku-4-5-20251001"
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        message = client.messages.create(
            model=model,
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
        summary = message.content[0].text.strip()
        logger.info("Anthropic summary OK (model=%s, chars=%d)", model, len(summary))
        return summary
    except Exception as exc:
        logger.warning("Anthropic summariser failed: %s", exc)
        return None


def _summarise_openai(text: str, title: str) -> Optional[str]:
    """Call OpenAI gpt-4o-mini."""
    if not settings.openai_api_key:
        return None
    try:
        from openai import OpenAI  # type: ignore

        model = "gpt-4o-mini"
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.chat.completions.create(
            model=model,
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
        summary = response.choices[0].message.content.strip()
        logger.info("OpenAI summary OK (model=%s, chars=%d)", model, len(summary))
        return summary
    except Exception as exc:
        logger.warning("OpenAI summariser failed: %s", exc)
        return None


def _summarise_mistral(text: str, title: str) -> Optional[str]:
    """Call Mistral AI — mistral-small-latest."""
    if not settings.mistral_api_key:
        return None
    try:
        from mistralai import Mistral  # type: ignore

        model = "mistral-small-latest"
        client = Mistral(api_key=settings.mistral_api_key)
        response = client.chat.complete(
            model=model,
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
        summary = response.choices[0].message.content.strip()
        logger.info("Mistral summary OK (model=%s, chars=%d)", model, len(summary))
        return summary
    except Exception as exc:
        logger.warning("Mistral summariser failed: %s", exc)
        return None


def _summarise_together(text: str, title: str) -> Optional[str]:
    """Call Together AI — Llama-3.3-70B-Instruct-Turbo."""
    if not settings.together_api_key:
        return None
    try:
        from together import Together  # type: ignore

        model = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
        client = Together(api_key=settings.together_api_key)
        response = client.chat.completions.create(
            model=model,
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
        summary = response.choices[0].message.content.strip()
        logger.info("Together summary OK (model=%s, chars=%d)", model, len(summary))
        return summary
    except Exception as exc:
        logger.warning("Together AI summariser failed: %s", exc)
        return None


def _summarise_gemini(text: str, title: str) -> Optional[str]:
    """Call Gemini 2.0 Flash."""
    if not settings.gemini_api_key:
        return None
    try:
        import google.generativeai as genai  # type: ignore

        model = "gemini-2.0-flash"
        genai.configure(api_key=settings.gemini_api_key)
        gmodel = genai.GenerativeModel(model)
        response = gmodel.generate_content(
            _PROMPT_TEMPLATE.format(title=title, text=text[:_MAX_INPUT_CHARS])
        )
        summary = response.text.strip()
        logger.info("Gemini summary OK (model=%s, chars=%d)", model, len(summary))
        return summary
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

    Falls back through: Groq → Anthropic → OpenAI → Mistral → Together → Gemini → Extractive.
    """
    if not text.strip():
        return title or "No content available."

    for provider_fn in (
        _summarise_groq,
        _summarise_anthropic,
        _summarise_openai,
        _summarise_mistral,
        _summarise_together,
        _summarise_gemini,
    ):
        result = provider_fn(text, title)
        if result:
            return result

    return _summarise_extractive(text, title)
