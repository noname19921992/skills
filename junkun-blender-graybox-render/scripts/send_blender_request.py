"""Submit one structured operation or explicitly high-risk Python request."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from pathlib import Path

from protocol_common import (
    PROTOCOL_VERSION,
    atomic_write_json,
    read_json,
    sha256_text,
    write_state,
)

OPERATIONS = {
    "inspect_scene",
    "save_copy",
    "upsert_camera",
    "render_review_frames",
    "export_shot_manifest",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge-dir", required=True)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--operation", choices=sorted(OPERATIONS))
    choice.add_argument("--code-file")
    parser.add_argument("--args-json", default="{}", help="JSON object for a structured operation")
    parser.add_argument("--allow-high-risk-code", action="store_true")
    parser.add_argument("--ttl", type=float, default=120.0)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--no-wait", action="store_true")
    return parser.parse_args()


def acquire_client_lock(root: Path) -> Path:
    lock = root / "client.lock"
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise SystemExit(f"Another client is submitting a request: {lock}") from exc
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(json.dumps({"pid": os.getpid(), "timestamp": time.time()}))
    return lock


def main() -> int:
    args = parse_args()
    if args.ttl <= 0 or args.timeout < 0:
        raise SystemExit("--ttl must be positive and --timeout cannot be negative")

    bridge = Path(args.bridge_dir).resolve()
    config = read_json(bridge / "bridge_config.json")
    if not isinstance(config, dict):
        raise SystemExit("Bridge protocol v2 is not prepared: bridge_config.json is missing")
    token = config.get("token")
    if not isinstance(token, str) or not token:
        raise SystemExit("Bridge configuration has no authentication token")
    if not (bridge / "connected.json").exists():
        raise SystemExit("Blender bridge is not connected: connected.json is missing")

    request_id = str(uuid.uuid4())
    created_at = time.time()
    request = {
        "protocol": PROTOCOL_VERSION,
        "id": request_id,
        "token": token,
        "created_at": created_at,
        "expires_at": created_at + args.ttl,
        "kind": "operation" if args.operation else "code",
        "operation": args.operation,
        "args": {},
        "code": None,
        "code_sha256": None,
        "high_risk": False,
    }

    if args.operation:
        try:
            operation_args = json.loads(args.args_json)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"--args-json is invalid JSON: {exc}") from exc
        if not isinstance(operation_args, dict):
            raise SystemExit("--args-json must decode to an object")
        request["args"] = operation_args
    else:
        if not args.allow_high_risk_code:
            raise SystemExit("Arbitrary Python requires --allow-high-risk-code")
        code_path = Path(args.code_file).resolve()
        code = code_path.read_text(encoding="utf-8")
        request.update({"code": code, "code_sha256": sha256_text(code), "high_risk": True})

    lock = acquire_client_lock(bridge)
    try:
        response_path = bridge / "responses" / f"{request_id}.json"
        request_path = bridge / "requests" / f"{request_id}.json"
        if response_path.exists() or request_path.exists():
            raise SystemExit(f"Request id collision: {request_id}")
        write_state(bridge, request_id, "queued", kind=request["kind"], operation=request["operation"])
        atomic_write_json(request_path, request)
    finally:
        lock.unlink(missing_ok=True)

    queued = {"id": request_id, "state": "queued", "request": str(request_path)}
    if args.no_wait:
        print(json.dumps(queued, ensure_ascii=False, indent=2))
        return 0

    deadline = time.monotonic() + args.timeout
    while time.monotonic() < deadline:
        response = read_json(response_path)
        if isinstance(response, dict) and response.get("id") == request_id:
            print(json.dumps(response, ensure_ascii=False, indent=2))
            return 0 if response.get("state") == "completed" else 1
        time.sleep(0.1)

    state = read_json(bridge / "states" / f"{request_id}.json", {})
    print(json.dumps({
        **queued,
        "timed_out": True,
        "last_known_state": state.get("state"),
        "status_command": f'{Path(sys.executable)} {Path(__file__).with_name("request_status.py")} --bridge-dir "{bridge}" --request-id {request_id}',
        "warning": "Timeout is an unknown outcome. Inspect status before cancelling or retrying.",
    }, ensure_ascii=False, indent=2))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
