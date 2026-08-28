"""Talk to a Gemma 4 model that is already on this laptop.

Ollama serves the weights at http://127.0.0.1:11434.
Nothing in this file calls Google's cloud.
"""

from __future__ import annotations

import os

import httpx

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
GEMMA_LOCAL_MODEL = os.getenv("GEMMA_LOCAL_MODEL", "gemma4:e2b")


class LocalGemmaError(RuntimeError):
    pass


def ollama_status() -> dict:
    try:
        tags = httpx.get(f"{OLLAMA_HOST}/api/tags", timeout=2.0).json()
        names = [m.get("name", "") for m in tags.get("models", [])]
        return {
            "ok": True,
            "host": OLLAMA_HOST,
            "model": GEMMA_LOCAL_MODEL,
            "pulled": any(GEMMA_LOCAL_MODEL in n or n.startswith(GEMMA_LOCAL_MODEL) for n in names),
            "models": names[:12],
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "host": OLLAMA_HOST,
            "model": GEMMA_LOCAL_MODEL,
            "pulled": False,
            "error": str(exc),
        }


def gemma_generate(prompt: str) -> str:
    """One local Gemma 4 completion. Weights never leave the machine."""
    try:
        response = httpx.post(
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model": GEMMA_LOCAL_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "options": {"temperature": 0.2, "num_ctx": 8192},
            },
            timeout=180.0,
        )
    except httpx.ConnectError as exc:
        raise LocalGemmaError(
            "Ollama is not running. Install it from https://ollama.com then run: ollama pull gemma4:e2b && ollama serve"
        ) from exc
    if response.status_code == 404:
        raise LocalGemmaError(
            f"Model {GEMMA_LOCAL_MODEL} is not pulled. Run: ollama pull {GEMMA_LOCAL_MODEL}"
        )
    response.raise_for_status()
    data = response.json()
    text = (data.get("message") or {}).get("content") or data.get("response") or ""
    if not text.strip():
        raise LocalGemmaError("Local Gemma returned an empty reply")
    return text.strip()
