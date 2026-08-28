"""Programmatic runner used by the FastAPI UI.

Live path talks only to local Gemma 4 through Ollama.
Sample path is the offline fallback if Ollama is not installed yet.
"""

from __future__ import annotations

import json
import os
import re
import traceback
from typing import Any

from dotenv import load_dotenv

from .local_gemma import GEMMA_LOCAL_MODEL, LocalGemmaError, gemma_generate, ollama_status
from .prompts import CODE_JUDGE, CREATIVITY_JUDGE, DEMO_JUDGE, STEWARD_INGEST, VERDICT_WRITER
from .tools import fetch_demo_evidence, fetch_github_evidence

load_dotenv()

SAMPLE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample_verdict.json")


def _extract_json(text: str) -> dict[str, Any]:
    if not text:
        raise ValueError("empty model response")
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).removesuffix("```").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise
        return json.loads(match.group(0))


def build_user_prompt(payload: dict[str, str]) -> str:
    return "\n".join([
        f"Project name: {payload.get('name') or 'Untitled'}",
        f"Repository URL: {payload.get('repo_url') or 'none'}",
        f"Demo URL: {payload.get('demo_url') or 'none'}",
        f"Pitch:\n{payload.get('pitch') or '(none provided)'}",
    ])


def gather_evidence(payload: dict[str, str]) -> dict[str, Any]:
    evidence: dict[str, Any] = {
        "name": payload.get("name") or "Untitled",
        "repo_url": payload.get("repo_url") or "",
        "demo_url": payload.get("demo_url") or "",
        "pitch": payload.get("pitch") or "",
    }
    if payload.get("repo_url"):
        try:
            evidence["github"] = json.loads(fetch_github_evidence(payload["repo_url"]))
        except Exception as exc:  # noqa: BLE001
            evidence["github"] = {"error": str(exc)}
    if payload.get("demo_url"):
        try:
            evidence["demo"] = json.loads(fetch_demo_evidence(payload["demo_url"]))
        except Exception as exc:  # noqa: BLE001
            evidence["demo"] = {"error": str(exc)}
    return evidence


def run_local_panel(payload: dict[str, str]) -> dict[str, Any]:
    evidence = gather_evidence(payload)
    evidence_json = json.dumps(evidence, ensure_ascii=False)[:12000]
    ingest_notes = gemma_generate(
        f"{STEWARD_INGEST}\n\nUSER SUBMISSION:\n{build_user_prompt(payload)}\n\nTOOL OUTPUT:\n{evidence_json}"
    )

    def judge(instruction: str) -> dict[str, Any]:
        raw = gemma_generate(
            f"{instruction}\n\nEVIDENCE PACK:\n{ingest_notes}\n\nRAW TOOL JSON:\n{evidence_json}"
        )
        return _extract_json(raw)

    code = judge(CODE_JUDGE)
    demo = judge(DEMO_JUDGE)
    creativity = judge(CREATIVITY_JUDGE)
    verdict_raw = gemma_generate(
        f"{VERDICT_WRITER}\n\nEVIDENCE:\n{ingest_notes}\n\n"
        f"CODE_OPINION:\n{json.dumps(code)}\n\n"
        f"DEMO_OPINION:\n{json.dumps(demo)}\n\n"
        f"CREATIVITY_OPINION:\n{json.dumps(creativity)}"
    )
    verdict = _extract_json(verdict_raw)
    verdict.setdefault("panel", {})
    verdict["panel"]["code"] = code
    verdict["panel"]["demo"] = demo
    verdict["panel"]["creativity"] = creativity
    verdict["models"] = {
        "runtime": "ollama-local",
        "judges": GEMMA_LOCAL_MODEL,
        "steward": GEMMA_LOCAL_MODEL,
        "orchestration": "Local Gemma ingest -> three local Gemma judges -> local Gemma verdict",
        "ollama": ollama_status(),
    }
    verdict["evidence_excerpt"] = ingest_notes[:1500]
    return verdict


def load_sample() -> dict[str, Any]:
    with open(SAMPLE_PATH, encoding="utf-8") as handle:
        return json.load(handle)


def run_jury(payload: dict[str, str], *, sample: bool = False) -> dict[str, Any]:
    if sample or os.getenv("DEMO_MODE", "").lower() in {"1", "true", "yes"}:
        data = load_sample()
        data["mode"] = "sample"
        data["models"] = {
            "runtime": "sample-fallback",
            "judges": GEMMA_LOCAL_MODEL,
            "note": "Recorded docket. Click Convene the panel after ollama pull gemma4:e2b to run live local Gemma.",
        }
        return data
    status = ollama_status()
    if not status.get("ok") or not status.get("pulled"):
        data = load_sample()
        data["mode"] = "sample_ollama_missing"
        data["note"] = (
            "Local Gemma is not ready. Install Ollama, run `ollama pull gemma4:e2b`, "
            "keep `ollama serve` running, then click Convene the panel."
        )
        data["error"] = status.get("error") or f"model not pulled: {GEMMA_LOCAL_MODEL}"
        data["models"] = {"runtime": "ollama-missing", "ollama": status}
        return data
    try:
        verdict = run_local_panel(payload)
        verdict["mode"] = "live-local-gemma"
        return verdict
    except (LocalGemmaError, Exception) as exc:  # noqa: BLE001
        data = load_sample()
        data["mode"] = "sample_after_error"
        data["error"] = str(exc)
        data["trace"] = traceback.format_exc()[-1500:]
        return data
