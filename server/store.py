"""Optional Firestore docket store. Falls back to an in-memory list."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Any

_MEMORY: list[dict[str, Any]] = []


def _collection_name() -> str:
    return os.getenv("FIRESTORE_COLLECTION", "gemmajury_dockets")


def save_docket(payload: dict[str, Any], verdict: dict[str, Any]) -> dict[str, Any]:
    record = {
        "id": uuid.uuid4().hex[:12],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
        "verdict": verdict,
        "backend": "memory",
    }
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    if project:
        try:
            from google.cloud import firestore

            client = firestore.Client(project=project)
            ref = client.collection(_collection_name()).document(record["id"])
            ref.set(record | {"backend": "firestore"})
            record["backend"] = "firestore"
            return record
        except Exception as exc:  # noqa: BLE001
            record["firestore_error"] = str(exc)
    _MEMORY.insert(0, record)
    return record


def list_dockets(limit: int = 12) -> list[dict[str, Any]]:
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    if project:
        try:
            from google.cloud import firestore

            client = firestore.Client(project=project)
            docs = (
                client.collection(_collection_name())
                .order_by("created_at", direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream()
            )
            return [doc.to_dict() for doc in docs]
        except Exception:
            pass
    return _MEMORY[:limit]
