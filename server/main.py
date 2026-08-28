"""Cloud Run / local HTTP entrypoint."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from agents.local_gemma import GEMMA_LOCAL_MODEL, ollama_status
from agents.runner import run_jury
from server.store import list_dockets, save_docket

load_dotenv()

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"

app = FastAPI(title="GemmaJury", version="1.1.0")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


class JudgeRequest(BaseModel):
    name: str = Field(default="Untitled")
    repo_url: str = Field(default="")
    demo_url: str = Field(default="")
    pitch: str = Field(default="")
    sample: bool = False


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/healthz")
def healthz() -> dict:
    status = ollama_status()
    return {
        "ok": True,
        "runtime": "ollama-local",
        "judges": GEMMA_LOCAL_MODEL,
        "steward": GEMMA_LOCAL_MODEL,
        "ollama": status,
        "cloud_key_required": False,
    }


@app.post("/api/judge")
def judge(req: JudgeRequest) -> dict:
    payload = req.model_dump()
    verdict = run_jury(payload, sample=req.sample)
    record = save_docket(payload, verdict)
    return {"docket_id": record["id"], "backend": record["backend"], "verdict": verdict}


@app.get("/api/dockets")
def dockets() -> dict:
    return {"dockets": list_dockets()}
