"""Shared helpers for Junkun Blender file-bridge protocol v2."""

from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from pathlib import Path
from typing import Any

PROTOCOL_VERSION = 2
TERMINAL_STATES = {"completed", "failed", "cancelled"}
TRANSITIONS = {
    None: {"queued"},
    "queued": {"accepted", "failed", "cancelled"},
    "accepted": {"running", "failed", "cancelled"},
    "running": {"completed", "failed"},
}


def read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    os.replace(temp, path)


def append_jsonl(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def valid_request_id(value: str) -> bool:
    try:
        return str(uuid.UUID(value)) == value.lower()
    except (ValueError, AttributeError):
        return False


def state_path(root: Path, request_id: str) -> Path:
    return root / "states" / f"{request_id}.json"


def write_state(root: Path, request_id: str, state: str, **extra: Any) -> dict[str, Any]:
    current = read_json(state_path(root, request_id), {}) or {}
    previous = current.get("state")
    if state != previous and state not in TRANSITIONS.get(previous, set()):
        raise ValueError(f"Invalid state transition: {previous!r} -> {state!r}")
    payload = {
        "protocol": PROTOCOL_VERSION,
        "id": request_id,
        "state": state,
        "previous_state": previous,
        "updated_at": time.time(),
        **extra,
    }
    atomic_write_json(state_path(root, request_id), payload)
    append_jsonl(root / "state_history" / f"{request_id}.jsonl", payload)
    return payload

