"""Model wiring.

Default path: Gemma 4 running locally through Ollama.
ADK agents use LiteLLM's ollama_chat provider so the same local weights are used.
"""

from __future__ import annotations

import os

from .local_gemma import GEMMA_LOCAL_MODEL, OLLAMA_HOST


def _env(name: str, default: str) -> str:
    value = os.getenv(name, default).strip()
    return value or default


def local_gemma_adk_model():
    from google.adk.models.lite_llm import LiteLlm

    return LiteLlm(model=f"ollama_chat/{GEMMA_LOCAL_MODEL}")


def gemma_judge_model():
    return local_gemma_adk_model()


def gemini_steward_model():
    """Steward is also local Gemma so the whole panel stays on-device."""
    return local_gemma_adk_model()


GEMMA_MODEL_ID = GEMMA_LOCAL_MODEL
GEMINI_MODEL_ID = f"local-gemma-steward/{GEMMA_LOCAL_MODEL}"
OLLAMA_URL = OLLAMA_HOST
