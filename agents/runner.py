"""Programmatic runner used by the FastAPI UI."""

from __future__ import annotations

import json
import os
import re
import traceback
from typing import Any

from dotenv import load_dotenv

from .models import GEMINI_MODEL_ID, GEMMA_MODEL_ID
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


def _genai_client():
    from google import genai

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing")
    return genai.Client(api_key=api_key)


def _generate(model: str, prompt: str) -> str:
    client = _genai_client()
    response = client.models.generate_content(model=model, contents=prompt)
    return (response.text or "").strip()


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


def run_direct_panel(payload: dict[str, str]) -> dict[str, Any]:
    evidence = gather_evidence(payload)
    evidence_json = json.dumps(evidence, ensure_ascii=False)[:20000]
    ingest_notes = _generate(
        GEMINI_MODEL_ID,
        f"{STEWARD_INGEST}\n\nUSER SUBMISSION:\n{build_user_prompt(payload)}\n\nTOOL OUTPUT:\n{evidence_json}",
    )

    def judge(instruction: str) -> dict[str, Any]:
        raw = _generate(
            GEMMA_MODEL_ID,
            f"{instruction}\n\nEVIDENCE PACK:\n{ingest_notes}\n\nRAW TOOL JSON:\n{evidence_json}",
        )
        return _extract_json(raw)

    code = judge(CODE_JUDGE)
    demo = judge(DEMO_JUDGE)
    creativity = judge(CREATIVITY_JUDGE)
    verdict_raw = _generate(
        GEMINI_MODEL_ID,
        f"{VERDICT_WRITER}\n\nEVIDENCE:\n{ingest_notes}\n\nCODE_OPINION:\n{json.dumps(code)}\n\nDEMO_OPINION:\n{json.dumps(demo)}\n\nCREATIVITY_OPINION:\n{json.dumps(creativity)}",
    )
    verdict = _extract_json(verdict_raw)
    verdict.setdefault("panel", {})
    verdict["panel"]["code"] = code
    verdict["panel"]["demo"] = demo
    verdict["panel"]["creativity"] = creativity
    verdict["models"] = {
        "steward": GEMINI_MODEL_ID,
        "judges": GEMMA_MODEL_ID,
        "orchestration": "Sequential ingest -> Parallel Gemma panel -> Gemini verdict",
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
        return data
    if not os.getenv("GEMINI_API_KEY"):
        data = load_sample()
        data["mode"] = "sample_no_key"
        data["note"] = "No GEMINI_API_KEY set — showing the recorded self-verdict."
        return data
    try:
        verdict = run_direct_panel(payload)
        verdict["mode"] = "live"
        return verdict
    except Exception as exc:  # noqa: BLE001
        data = load_sample()
        data["mode"] = "sample_after_error"
        data["error"] = str(exc)
        data["trace"] = traceback.format_exc()[-1500:]
        return data
