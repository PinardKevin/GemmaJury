"""Model wiring.

Gemma 4 is the specialist panel. Gemini 3.5 is only the steward.
Both are reached through the Gemini API so a single GEMINI_API_KEY works.
"""

from __future__ import annotations

import os

from google.adk.models import Gemini


def _env(name: str, default: str) -> str:
    value = os.getenv(name, default).strip()
    return value or default


def gemma_judge_model() -> Gemini:
    return Gemini(model=_env("GEMMA_JUDGE_MODEL", "gemma-4-31b-it"))


def gemini_steward_model() -> Gemini:
    return Gemini(model=_env("GEMINI_STEWARD_MODEL", "gemini-3.5-flash"))


GEMMA_MODEL_ID = _env("GEMMA_JUDGE_MODEL", "gemma-4-31b-it")
GEMINI_MODEL_ID = _env("GEMINI_STEWARD_MODEL", "gemini-3.5-flash")
